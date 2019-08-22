from weixin import WeChat, RedisUse
from flask import Flask, request, redirect, jsonify
import requests
import urllib.request
import urllib.parse
import json


appID = "wx1b26e33bc6d53859"
AppSecret = "fd82140b782c9508b76fa276f13a8d44"
app = Flask(__name__)


# 获取微信服务号code
@app.route('/getWeiXin')
def getCode():
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
    #     refresh_token=res_json["refresh_token"]
    #     openid = res_json["openid"]
    #     getRefreshToken=urllib.request.Request(url_retoken.format(appid=appID, refresh_token=refresh_token))
    #     res_data = urllib.request.urlopen(getRefreshToken)
    #     res_reToken = res_data.read().decode('utf-8')
    #     res_json = json.loads(res_reToken)  # 转成json
    #     access_token = res_json["access_token"]
    #     getUserInfo = urllib.request.Request(url_info.format(access_token=access_token, openid=openid))
    #     res_data = urllib.request.urlopen(getUserInfo)
    #     res = res_data.read().decode('utf-8')
    #     return json.dumps(res)
    code = request.args.get('code')
    wx = WeChat()
    result = wx.getCode(code)

    return result


@app.route('/setcode')
def setCode():
    pre_url = 'http://api.qihaoyu.tech/jws/wans'
    scope = 'snsapi_userinfo'
    again_url = '?validate=userinfo&url=http://api.qihaoyu.tech/jws/jiexi'
    wx = WeChat()
    weixin = wx.setCode(pre_url, scope, again_url)
    return redirect(weixin)


@app.route('/jiexi')
def jiexi():
    # data = {
    #     'openid': 'ocyjVv9AuNf4JVjja6zlIIY5IfO8 ',
    #     'nickname': '\u8c22\u6b23\u6211\u5927\u54e5',
    #     'sex': 1,
    #     'language': 'zh_CN',
    #     'city': '\u798f\u5dde',
    #     'province': '\u798f\u5efa',
    #     'country': '\u4e2d\u56fd',
    #     'headimgurl': 'http:\\/\\/thirdwx.qlogo.cn\\/mmopen\\/vi_32\\/7U5fWt1mEsFkkxepQjBHCc2wemYKAtnicXpsGgDPcyrzKLe01tZNiaD6RNMQ0wy68KBMmFLV4ss5daxV9hUCvDzg\\/132\ ',
    #     'privilege': [],
    #     }
    sr = RedisUse()
    result = sr.insertToken('token', 'openid')
    # result = json.dumps(data)
    if result:
        return json.dumps(1)
    else:
        return json.dumps(2)


if __name__ == '__main__':
    # app.run(host="服务器地址",post=端口号,debug模式)
    app.run(port='5000', debug=True)

