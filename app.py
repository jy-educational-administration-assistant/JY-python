from __future__ import absolute_import, unicode_literals
from flask import Flask, request, jsonify, redirect
from school_api import SchoolClient
import urllib.request
import urllib.parse
import json
from weixin import WX

app = Flask(__name__)
school = SchoolClient('http://jws.hebiace.edu.cn/default2.aspx')


@app.route('/get_score')
def get_score():
    # 获取成绩
    # http://127.0.0.1:5000/get_score?account=20173250131&passwd=350429yyq
    account = request.args.get("account")
    passwd = request.args.get("passwd")
    user = school.user_login(account, passwd)
    school_data = user.get_score(use_api=3)
    return jsonify(school_data)


@app.route('/get_student_info')
def get_student_info():
    # 获取学生个人信息
    # http://127.0.0.1:5000/get_student_info?account=20173400117&passwd=130132wzf
    account = request.args.get("account")
    passwd = request.args.get("passwd")
    user = school.user_login(account, passwd)
    student_info = user.get_student_info()
    return jsonify(student_info)


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
def setCode():
    pre_url = 'http://api.qihaoyu.tech/jws/getcode'
    scope = 'snsapi_userinfo'
    again_url = '?validate=userinfo&url=http://api.qihaoyu..tech/jws/setcode'
    wx = WX()
    weixin = wx.setCode(pre_url, scope, again_url)
    return redirect(weixin)


@app.route('/getcode')
def getCode():
    # appID = "wx1b26e33bc6d53859"
    # AppSecret = "fd82140b782c9508b76fa276f13a8d44"
    # url_code = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={appsecret}&code={code}&grant_type=authorization_code"
    # url_retoken = "https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={appid}&grant_type=refresh_token&refresh_token={refresh_token}"
    # url_info = "https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
    # code = request.args.get('code')
    # if code:
    #     accessToken = urllib.request.Request(url_code.format(appid=appID, appsecret=AppSecret, code=code))
    #     res_data = urllib.request.urlopen(accessToken)
    #     res = res_data.read().decode('utf-8')
    #     res_json = json.loads(res)#转成json
    #     access_token = res_json["access_token"]
    #     refresh_token = res_json["refresh_token"]
    #     openid = res_json["openid"]
    #     getRefreshToken = urllib.request.Request(url_retoken.format(appid=appID, refresh_token=refresh_token))
    #     res_data = urllib.request.urlopen(getRefreshToken)
    #     res_reToken = res_data.read().decode('utf-8')
    #     res_json = json.loads(res_reToken)  # 转成json
    #     access_token = res_json["access_token"]
    #     getUserInfo = urllib.request.Request(url_info.format(access_token=access_token, openid=openid))
    #     res_data = urllib.request.urlopen(getUserInfo)
    #     res = res_data.read().decode('utf-8')
        code = request.args.get('code')
        again_url = request.args.get('url')
        wx = WX()
        res = wx.getCode(code)
        return json.dumps(res+again_url)



if __name__ == '__main__':
    app.run(debug=True)
