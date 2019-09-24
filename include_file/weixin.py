import json
import urllib.parse
import urllib.request

appID = "xxx"
AppSecret = "xxx"


class WeChat(object):
    def setCode(self, pre_url, scope, again_url):
        data = {
            'redirect_uri': pre_url + again_url,
            'appid': appID,
            'response_type': 'code',
            'scope': scope,
            'state': '123',
        }
        urlencode = urllib.parse.urlencode(data)
        wx_open = 'https://open.weixin.qq.com/connect/oauth2/authorize?' + urlencode + '#wechat_redirect'
        return wx_open

    def getCode(self, code):
        url_code = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={appsecret}&code={code}&grant_type=authorization_code"
        url_retoken = "https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={appid}&grant_type=refresh_token&refresh_token={refresh_token}"
        url_info = "https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
        if code:
            accessToken = urllib.request.Request(url_code.format(appid=appID, appsecret=AppSecret, code=code))
            res_data = urllib.request.urlopen(accessToken)
            res = res_data.read().decode('utf-8')
            res_json = json.loads(res)  # 转成json
            access_token = res_json["access_token"]
            refresh_token = res_json["refresh_token"]
            openid = res_json["openid"]
            getRefreshToken = urllib.request.Request(url_retoken.format(appid=appID, refresh_token=refresh_token))
            res_data = urllib.request.urlopen(getRefreshToken)
            res_reToken = res_data.read().decode('utf-8')
            res_json = json.loads(res_reToken)  # 转成json
            access_token = res_json["access_token"]
            getUserInfo = urllib.request.Request(url_info.format(access_token=access_token, openid=openid))
            res_data = urllib.request.urlopen(getUserInfo)
            res = res_data.read().decode('utf-8')

            return res




