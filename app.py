from __future__ import absolute_import, unicode_literals
from flask import Flask, request, jsonify, redirect
from school_api import SchoolClient
from weixin import WeChat, RedisUse
import requests
import time
import hashlib
import urllib.request
import urllib.parse
import json

app = Flask(__name__)
school = SchoolClient('http://jws.hebiace.edu.cn/default2.aspx')


@app.route('/get_student_info')
def get_student_info():
    # 获取学生个人信息
    # http://127.0.0.1:5000/get_student_info?account=20173400117&passwd=130132wzf
    account = request.args.get("account")
    passwd = request.args.get("passwd")
    user = school.user_login(account, passwd)
    student_info = user.get_student_info()
    return jsonify(student_info)


@app.route('/get_score')
def get_score():
    # 获取成绩
    # http://127.0.0.1:5000/get_score?account=20173250131&passwd=350429yyq
    account = request.args.get("account")
    passwd = request.args.get("passwd")
    user = school.user_login(account, passwd)
    school_data = user.get_score(use_api=3)
    return jsonify(school_data)


@app.route('/get_schedule')
def get_schedule():
    # 获取课表
    # http://127.0.0.1:5000/get_schedule?account=20173250131&passwd=350426yyq&schedule_year=2019-2020&schedule_term=1
    account = request.args.get("account")
    passwd = request.args.get("passwd")
    user = school.user_login(account, passwd)
    schedule_year = request.args.get("schedule_year")
    schedule_term = request.args.get("schedule_term")
    schedule_type = 1
    schedule_data = user.get_schedule(schedule_year, schedule_term, schedule_type)
    return jsonify(schedule_data)


@app.route('/set_code')
def set_code():
    pre_url = 'http://api.qihaoyu.tech/jws/get_code'
    scope = 'snsapi_userinfo'
    again_url = '?validate=userinfo&url=http://api.qihaoyu..tech/jws/set_code'
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
                url = 'http://myserver.qihaoyu.tech'
                obj = redirect(url)
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


@app.route('/get_cookies')
def get_cookies():
    url = "http://api.qihaoyu.tech/jws/get_score"
    session = requests.Session()
    response = session.get(url)
    # html_set_cookie = requests.utils.dict_from_cookiejar(session.cookies)
    r = session.cookies.get_dict()
    return jsonify(r)


@app.route('/user_binding', methods=['GET', 'POST'])
def user_binding():
    sr = RedisUse()
    token = request.form.get('token')
    openid = sr.getTokenOpenid(token)
    student_id = request.form.get('student_id')
    password = request.form.get('password')
    data = {
        'student_id': student_id,
        'password': password,
    }
    redis_result_id_password = sr.insertOpenidData(openid, data)
    if not redis_result_id_password:
        data_redis_none = {
                   'code': 1,
                   'msg': 'redis数据库错误，请联系管理员'
        }
        return data_redis_none
    data = {
        'code': 0
    }
    return data

@app.route('/hello', methods=['GET'])
def hello():
    return 'hello world'

@app.route('/test_set_cookie', methods=['GET'])
def test_set_cookie():
    resp = make_response('set_cookie')
    resp.set_cookie('passwd', '123456')
    return resp


@app.route('/test_get_cookie', methods=['GET'])
def test_get_cookie():
    name = request.cookies.get('name')
    return name


if __name__ == '__main__':
    app.run(port='5000', debug=True)
