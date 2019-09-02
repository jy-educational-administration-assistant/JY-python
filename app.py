from __future__ import absolute_import, unicode_literals
from weixin import WeChat, RedisUse, MysqlUse, UserApply
from flask import Flask, request, jsonify, redirect
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
    # 获取学生个人信息
    # http://127.0.0.1:5000/get_student_info?account=20173400117&password=130132wzf
    # account = request.args.get("account")
    # password = request.args.get("password")
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
        student_info = user.get_student_info()
        return jsonify(student_info)


@app.route('/get_score')
def get_score():
    # 获取成绩
    # http://127.0.0.1:5000/get_score?account=20173250131&password=350429yyq
    score_year = request.args.get('year')
    score_term = request.args.get('term')
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
        school_data = user.get_score(score_year, score_term, use_api=3)
        return jsonify(school_data)


@app.route('/get_schedule')
def get_schedule():
    # 获取课表
    # http://127.0.0.1:5000/get_score?account=20173250131&password=350429yyq&
    # account = request.args.get("account")
    # password = request.args.get("password")
    schedule_year = request.args.get('year')
    schedule_term= request.args.get('term')
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
        redis_result_nature = sr.getOpenidNatureAll(openid)
        if not redis_result_nature:
            data_redis_none = {
                'code': 1,
                'msg': 'redis数据库错误，请联系管理员'
            }
            return data_redis_none
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
                'classroom': ''
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


@app.route('/test', methods=['POST', 'GET'])
def test():
    # pre_url = url + '/api/get_code'
    # again_url = '?validate=userinfo&url='+url+'/api/set_code'
    # return jsonify({
    #     'pre_url': pre_url,
    #     'again_url': again_url,
    # })
    # http://127.0.0.1/test?account=20173250131&password=350426yyq
    openid = 'ocyjVv9AuNf4JVjja6zlIIY5IfO8'
    db = MysqlUse()
    use = UserApply()
    res = db.selectStudentMessage('openid', openid)
    account = res[0][0]
    password = res[0][1]
    res = use.get_student_message(account, password)
    return jsonify(res)


@app.route('/hello', methods=['GET'])
def hello():
    return 'hello world'

@app.route('/test_set_cookie', methods=['GET'])
def test_set_cookie():
    # resp = make_response('set_cookie')
    # resp.set_cookie('passwd', '123456')
    return jsonify(1)


@app.route('/test_get_cookie', methods=['GET'])
def test_get_cookie():
    name = request.cookies.get('name')
    return name


if __name__ == '__main__':
    app.run(port='5000', debug=True)
