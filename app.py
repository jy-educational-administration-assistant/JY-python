from __future__ import absolute_import, unicode_literals
from flask import Flask, request, jsonify, redirect, make_response
from include_file.schoolapiget import SchoolApiGet
from include_file.redisuse import RedisUse
from include_file.sqluse import MysqlUse
from include_file.weixin import WeChat
from include_file.user import UseApply
import hashlib
import time
import json


app = Flask(__name__)
url = 'http://jws.qihaoyu.tech'


@app.route('/get_student_info')
def get_student_info():
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        sr = RedisUse()
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        db = MysqlUse()
        sch = SchoolApiGet()
        res = db.selectStudentMessage('openid', openid)
        if not res:
            return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
        if res[0][4] and res[0][6] and res[0][7] and res[0][8]:
            data_res = {
                "student_name": res[0][4],
                "student_xy": res[0][6],
                "student_xzb": res[0][8],
                "student_zy": res[0][7],
                "img": res[0][11],
            }
            data = {
                'code': 0,
                'data': data_res,
            }
            return jsonify(data)
        else:
            account = res[0][1]
            password = res[0][2]
            student_info = sch.get_student(account, password)
            if 'error' in student_info:
                return jsonify({
                    'code': 1,
                    'msg': student_info
                })
            res_sql = db.insertStudentOther(openid, student_info)
            if res_sql:
                res = db.selectStudentMessage('openid', openid)
                data_res = {
                    "student_name": res[0][4],
                    "student_xy": res[0][6],
                    "student_xzb": res[0][8],
                    "student_zy": res[0][7],
                    "img": res[0][11],
                }
                data = {
                    'code': 0,
                    'data': data_res,
                }
                return jsonify(data)
            else:
                data = {
                    'code': 1,
                    'msg': 'sql运行错误，请联系管理员'
                }
                return jsonify(data)


@app.route('/get_score')
def get_score():
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        sr = RedisUse()
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        db = MysqlUse()
        sch = SchoolApiGet()
        use = UseApply()
        res = db.selectStudentMessage('openid', openid)
        if not res:
            return jsonify({'code': 1, 'msg': '查找sql错误，请联系管理员'})
        account = res[0][1]
        password = res[0][2]
        point = res[0][9]
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
                    sql_res_point = db.selectStudentMessage('account', account)
                    res_score = use.manageScore(sql_res_score)
                    data = {
                        'code': 0,
                        'data': res_score,
                        'point': sql_res_point[0][9],
                    }
                    return jsonify(data)
                else:
                    data = {
                        'code': 1,
                        'msg': '查找成绩sql错误，请联系管理员',
                        'other': sql_res,
                    }
                    return jsonify(data)
            else:
                data = {
                    'code': 1,
                    'msg': sql_res
                }
                return jsonify(data)
        else:
            if point:
                sql_res_score = db.selectScore(account, data_query_score)
                sql_res_point = db.selectStudentMessage('account', account)
                res_score = use.manageScore(sql_res_score)
                data = {
                    'code': 0,
                    'data': res_score,
                    'point': sql_res_point[0][9],
                }
                return jsonify(data)
            else:
                school_data = sch.get_score_info(account, password)
                res_allcollege_point = db.updateStudentMessage('account', account, 'all_point', school_data['all_college']['pjzjd'])
                if not res_allcollege_point:
                    return jsonify({'code': 1, 'msg': 'sql数据库错误'})
                res_allcollege_major_num = db.updateStudentMessage('account', account, 'major_number', school_data['all_college']['zyzrs'])
                if not res_allcollege_major_num:
                    return jsonify({'code': 1, 'msg': 'sql数据库错误'})
                sql_res_score = db.selectScore(account, data_query_score)
                sql_res_point = db.selectStudentMessage('account', account)
                res_score = use.manageScore(sql_res_score)
                data = {
                    'code': 0,
                    'data': res_score,
                    'point': sql_res_point[0][9],
                }
                return jsonify(data)


@app.route('/get_schedule')
def get_schedule():
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        sr = RedisUse()
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        schedule_year = request.args.get('year')
        schedule_term = request.args.get('term')
        if schedule_term is None or schedule_year is None:
            return jsonify({'code': 1, 'msg': '参数错误'})
        use = UseApply()
        db = MysqlUse()
        res = db.selectStudentMessage('openid', openid)
        account = res[0][1]
        password = res[0][2]
        classroom = res[0][8]
        validate_schedule = db.selectSchedule(classroom, schedule_year, schedule_term)
        if not validate_schedule:
            sql_reschedule = use.getSchedule(account, password, classroom, schedule_year, schedule_term)
            if not sql_reschedule:
                data = {
                    'code': 1,
                    'msg': 'sql数据库错误，请联系管理员'
                }
                return jsonify(data)
            sql_res_schedule = db.selectSchedule(classroom, schedule_year, schedule_term)
            res_schedule = use.mangageSchedule(sql_res_schedule)
            data = {
                'code': 0,
                'data': res_schedule,
            }
            return jsonify(data)
        else:
            res_schedule = use.mangageSchedule(validate_schedule)
            data = {
                'code': 0,
                'data': res_schedule,
            }
            return jsonify(data)


@app.route('/set_code')
def set_code():
    pre_url = 'http://m.hebiace.net/app/wxGetUserInfo/getUserInfo.php'
    redirect_url = '?validate=userinfo&url=jws.qihaoyu.tech/api/get_code'
    scope = 'snsapi_userinfo'
    wx = WeChat()
    weixin = wx.setCode(pre_url, scope, redirect_url)
    return redirect(weixin)


@app.route('/get_code')
def get_code():
        openid = request.args.get('openid')
        if openid:
            img = request.args.get('img')
            nickname = request.args.get('name')
            sr = RedisUse()
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
                redirect_url = url
                obj = redirect(redirect_url)
                obj.set_cookie('token', token)

                return obj

            else:
                data = {
                    'code': 1,
                    'msg': 'redis数据库错误，请联系管理员'
                }
                return jsonify(data)

        else:
            again_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?&url=jws.qihaoyu.tech/api/get_code'
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
        if res_binding_openid:
            if res_binding_openid[0][1] and res_binding_openid[0][2]:
                data_isbinding = {
                    'isBind': 1,
                }
                data = {
                    'code': 0,
                    'data': data_isbinding,
                }
                return jsonify(data)
            else:
                data_isbinding = {
                    'isBind': 0,
                }
                data = {
                    'code': 0,
                    'data': data_isbinding,
                }
                return jsonify(data)
        else:
            data_isbinding = {
                'isBind': 0,
            }
            data = {
                'code': 0,
                'data': data_isbinding,
            }
            return jsonify(data)


@app.route('/user_binding', methods=['POST', 'GET'])
def user_binding():
    token = request.cookies.get('token')
    if not token:
        return jsonify({
            'code': 2,
        })
    else:
        sr = RedisUse()
        openid = sr.getTokenOpenid(token)
        if not openid:
            return jsonify({
                'code': 2,
            })
        db = MysqlUse()
        sch = SchoolApiGet()
        times = str(time.time()).split('.', 1)
        times = times[0]
        account = request.form.get('account')
        password = request.form.get('password')
        # account = request.args.get('account')
        # password = request.args.get('password')
        res = sch.validate_user(account, password)
        if res:
            return jsonify(res)
        res_sel = db.selectStudentMessage('openid', openid)
        if res_sel:
            res_account = db.updateStudentMessage('openid', openid, 'account', account)
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
                    'account': account,
                    'password': password,
                    'binding_time': times,
                    'major': 'NULL',
                    'email': 'NULL',
                    'college': 'NULL',
                    'full_name': 'NULL',
                    'img': redis_result_nature['img'],
                    'nickname': redis_result_nature['nickname'],
                    'openid': openid,
                    'classroom': 'NULL',
                    'all_point': 'NULL',
                    'major_number': 'NULL',
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
    res_untying = db.untyingStudent('openid', openid)
    if not res_untying:
        return jsonify({'code': 1, 'msg': 'sql错误，请联系管理员'})
    return jsonify({'code': 0})


@app.route('/test', methods=['POST', 'GET'])
def test():
    # db = MysqlUse()
    # use = UseApply()
    # all_student = db.selectStudentMessage()
    # for num in all_student:
    #     # print(num[0], num[1], num[2], num[8])
    #     res = use.updateSechdeuleinformation(num[1], num[2], num[8])
    return jsonify(1)


@app.route('/hello', methods=['GET'])
def hello():
    sch = SchoolApiGet()
    res = sch.get_schedule_info('20173250131', '350426yyq', '2019-2020', 1)
    return jsonify(res)


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
