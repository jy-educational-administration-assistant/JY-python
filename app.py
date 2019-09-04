from __future__ import absolute_import, unicode_literals
from weixin import WeChat, RedisUse, MysqlUse, UseApply
from flask import Flask, request, jsonify, redirect, make_response
from school_api import SchoolClient
from redis import Redis
from school_api.session.redisstorage import RedisStorage
import time
import hashlib
import json

app = Flask(__name__)
url = 'http://myserver.qihaoyu.tech'
redis = Redis()
session = RedisStorage(redis)
conf = {
    "url": 'http://jws.hebiace.edu.cn/default2.aspx',
    "session": session,
    'name': '河北建筑工程学院',
    'code': 'hbjg'
}

school = SchoolClient(**conf)


@app.route('/get_student_info')
def get_student_info():
    sr = RedisUse()
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        db = MysqlUse()
        i = 0
        res = db.selectStudentMessage('openid', openid)
        if not res:
            return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
        if res[0][2] is '' or res[0][8] is '' or res[0][9] is '' or res[0][10] is '':
            account = res[0][0]
            password = res[0][1]
            user = school.user_login(account, password)
            for i in 'res':
                student_info = user.get_student_info()
            res_sql = db.insertStudentOther(openid, student_info)
            if res_sql:
                res = db.selectStudentMessage('openid', openid)
                res_data = {
                    "student_name": res[0][9],
                    "student_xy": res[0][8],
                    "student_xzb": res[0][10],
                    "student_zy": res[0][2],
                    "img": res[0][6],
                }
                data = {
                    'code': 0,
                    'data': res_data,
                    'res_sql': res_sql,
                }
                return jsonify(data)
            else:
                data = {
                    'code': 1,
                    'msg': 'sql运行错误，请联系管理员'
                }
                return jsonify(data)
        else:
            data_res = {
                "student_name": res[0][9],
                "student_xy": res[0][8],
                "student_xzb": res[0][10],
                "student_zy": res[0][2],
                "img": res[0][6],
            }
            data = {
                'code': 0,
                'data': data_res,
            }
            return jsonify(data)


@app.route('/get_score')
def get_score():
    sr = RedisUse()
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        db = MysqlUse()
        use = UseApply()
        res = db.selectStudentMessage('openid', openid)
        if not res:
            return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
        account = res[0][0]
        password = res[0][1]
        score_year = request.args.get('year')
        score_term = request.args.get('term')
        data_query_score = {
            'year': score_year,
            'term': score_term,
        }
        validate_score = db.selectScore(account, {'term': None, 'year': None})
        if not validate_score:
            sql_res = use.getScore(account, password)
            if sql_res:
                sql_res_score = db.selectScore(account, data_query_score)
                if sql_res_score:
                    sql_res_point = db.selectStudentMessage('student_id', account)
                    data = {
                        'code': 0,
                        'data': sql_res_score,
                        'point': sql_res_point[0][11],
                    }
                    return jsonify(data)
                else:
                    data = {
                        'code': 1,
                        'msg': 'sql错误，请联系管理员'
                    }
                    return jsonify(data)
            else:
                data = {
                    'code': 1,
                    'msg': '数据库错误，请联系管理员'
                }
                return jsonify(data)
        else:
            sql_res_score = db.selectScore(account, data_query_score)
            sql_res_point = db.selectStudentMessage('student_id', account)
            data = {
                'code': 0,
                'data': sql_res_score,
                'point': sql_res_point[0][11],
            }
            return jsonify(data)


@app.route('/get_schedule')
def get_schedule():
    schedule_year = request.args.get('year')
    schedule_term = request.args.get('term')
    schedule_type = 1
    sr = RedisUse()
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        db = MysqlUse()
        res = db.selectStudentMessage('openid', openid)
        account = res[0][0]
        password = res[0][1]
        user = school.user_login(account, password)
        schedule_data = user.get_schedule(schedule_year, schedule_term, schedule_type)
        return jsonify(schedule_data)


@app.route('/set_code')
def set_code():
    pre_url = url + '/api/get_code'
    again_url = '?validate=userinfo&url='+url+'/api/set_code'
    scope = 'snsapi_userinfo'
    wx = WeChat()
    weixin = wx.setCode(pre_url, scope, again_url)
    print(weixin)
    return redirect(weixin)


@app.route('/get_code')
def get_code():
        code = request.args.get('code')
        again_url = request.args.get('url')
        wx = WeChat()
        sr = RedisUse()
        res = wx.getCode(code)
        if res:
            res = json.loads(res)
            openid = res['openid']
            img = res['headimgurl']
            nickname = res['nickname']
            time_now = str(int(time.time()))
            token = hashlib.new('md5', (openid+time_now).encode("utf-8"))
            token = token.hexdigest()
            redis_token_result = sr.insertTokenOpenid(token, openid)
            if redis_token_result:
                data_openid = {
                    'img': img,
                    'nickname': nickname,
                }
                redis_data_openid = sr.insertOpenidData(openid, data_openid)
                if not redis_data_openid:
                    data = {
                        'code': 1,
                        'msg': 'redis数据库错误，请联系管理员'
                     }
                    return jsonify(data)
                redict_url = url
                obj = redirect(redict_url)
                obj.set_cookie('token', token)

                return obj

            else:
                data = {
                    'code': 1,
                    'msg': 'redis数据库错误，请联系管理员'
                }
                return jsonify(data)

        else:
            redirect(again_url)


@app.route('/user_login')
def user_login():
    sr = RedisUse()
    db = MysqlUse()
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        res_binding_openid = db.selectStudentMessage('openid', openid)
        if not res_binding_openid:
            data_isbinding = {
                'isBind': 0,
            }
            data = {
                'code': 0,
                'data': data_isbinding
            }
            return jsonify(data)
        else:
            data_isbinding = {
                'isBind': 1,
            }
            data = {
                'code': 0,
                'data': data_isbinding,
            }
            return jsonify(data)


@app.route('/user_binding', methods=['POST', 'GET'])
def user_binding():
    sr = RedisUse()
    db = MysqlUse()
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        times = str(time.time()).split('.', 1)
        times = times[0]
        student_id = request.form.get('account')
        password = request.form.get('password')
        user = school.user_login(student_id, password, use_cookie_login=False)
        res = hasattr(user, 'tip')
        if res is True:
            data = {
                'code': 1,
                'msg': user.tip
            }
            return jsonify(data)
        res_sel = db.selectStudentMessage('openid', openid)
        if res_sel:
            res_account = db.updateStudentMessage('openid', openid,'student_id', student_id)
            if not res_account:
                return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
            res_password = db.updateStudentMessage('openid', openid, 'password', password)
            if not res_password:
                return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
            return jsonify({'code': 0})
        else:
            redis_result_nature = sr.getOpenidNatureAll(openid)
            if not redis_result_nature:
                data_redis_none = {
                    'code': 1,
                    'msg': 'redis数据库错误，请联系管理员'
                }
                return jsonify(data_redis_none)
            else:
                data_redis = {
                    'student_id': student_id,
                    'password': password,
                    'binding_time': times,
                    'major': '',
                    'email': '',
                    'college': '',
                    'full_name': '',
                    'img': redis_result_nature['img'],
                    'nickname': redis_result_nature['nickname'],
                    'openid': openid,
                    'classroom': '',
                    'all_point': '',
                    'major_number': '',
                }
                sql_result = db.insertStudentMessage(data_redis)
                if not sql_result:
                    data_res = {
                        'code': 1,
                        'msg': 'sql数据库添加错误，请联系管理员'
                    }
                    return jsonify(data_res)
                else:
                    data = {
                        'code': 0
                    }
                    return jsonify(data)


@app.route('/user_untying')
def user_untying():
    sr = RedisUse()
    db = MysqlUse()
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        openid = sr.getTokenOpenid(token)
    if not openid:
        return jsonify({
            'code': 2,
        })
    res_sel = db.selectStudentMessage('openid', openid)
    if not res_sel:
        return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
    res_account = db.updateStudentMessage('openid', openid, 'student_id', None,)
    if not res_account:
        data = {
            'code': 1,
            'msg': '数据库错误，请联系管理员'
        }
        return jsonify(data)
    res_password = db.updateStudentMessage('openid', openid, 'password', None,)
    if not res_password:
        data = {
            'code': 1,
            'msg': '数据库错误，请联系管理员'
        }
        return jsonify(data)
    return jsonify({'code': 0})


@app.route('/test', methods=['POST', 'GET'])
def test():
    # score_year = request.args.get('year')
    # score_term = request.args.get('term')
    openid = 'ocyjVv9AuNf4JVjja6zlIIY5IfO8'
    schedule_year = request.args.get('year')
    schedule_term = request.args.get('term')
    schedule_type = 1
    db = MysqlUse()
    use = UseApply()
    db = MysqlUse()
    res = db.selectStudentMessage('openid', openid)
    account = res[0][0]
    password = res[0][1]
    user = school.user_login(account, password)
    schedule_data = user.get_schedule(schedule_year, schedule_term, schedule_type)
    return jsonify(schedule_data)


@app.route('/hello', methods=['GET'])
def hello():
    return 'hello world'


@app.route('/test_set_cookie', methods=['GET'])
def test_set_cookie():
    resp = make_response()
    resp.set_cookie('passwd', '1595995')
    return resp


@app.route('/test_get_cookie', methods=['GET'])
def test_get_cookie():
    name = request.cookies.get('password')
    return name


if __name__ == '__main__':
    app.run(port='5000', debug=True)
