from __future__ import absolute_import, unicode_literals
from flask import Flask, request, jsonify, redirect
from school_api import SchoolClient
from weixin import WeChat, RedisUse
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


@app.route('/setcode')
def setcode():
    pre_url = 'http://api.qihaoyu.tech/jws/getcode'
    scope = 'snsapi_userinfo'
    again_url = '?validate=userinfo&url=http://api.qihaoyu..tech/jws/set_code'
    wx = WeChat()
    weixin = wx.setCode(pre_url, scope, again_url)
    return redirect(weixin)


@app.route('/getcode')
def getCode():
        code = request.args.get('code')
        again_url = request.args.get('url')
        wx = WeChat()
        sr = RedisUse()
        res = wx.getCode(code)
        if res:
            res = json.loads(res)
            return res['openid']
            # openid = res[0]['openid']
            # img = res['heardimgurl']
            # nickname = res['nickname']
            # data = {
            #     'openid': openid,
            #     'img': img,
            #     'nickname': nickname,
            # }
            # return jsonify(openid)
            # token = hashlib.md5(openid+time.time())
            # redis_result = sr.insertTokenOpenid(token, openid)
            # if redis_result:
            #     url = 'http://myserver.qihaoyu.tech?token={token}'.format(token=token)
            #     return redirect(url)
            # else:
            #     data = {
            #         'code': 1,
            #         'msg': 'redis数据库错误，请联系管理员'
            #     }
            #     return jsonify(data)
        else:
            redirect(again_url)


@app.route('/user_binding', methods=['POST'])
def user_binding():
    sr = RedisUse()
    token = request.form('token')
    openid  = sr.getTokenOpenid(token)
    student_id = request.form('student_id')
    password = request.form('password')


if __name__ == '__main__':
    app.run(debug=True)
