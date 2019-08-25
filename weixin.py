import urllib.request
import urllib.parse
from flask import Flask, request, redirect, jsonify
import json
from redis import StrictRedis
import pymysql

appID = "wx1b26e33bc6d53859"
AppSecret = "fd82140b782c9508b76fa276f13a8d44"


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


class RedisUse(object):
    def __init__(self):
        self.sr = StrictRedis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    def insertTokenOpenid(self, token, openid):
        res = self.sr.set(token, openid)
        res_time = self.sr.expire(token, 7200)

        return res

    def getTokenOpenid(self, token):
        res = self.sr.get(token)

        return res

    def insertOpenidData(self, openid, data):
        res = self.sr.hmset(openid, data)

        return res

    def selectOpenidNature(self, openid):
        res = self.sr.hkeys(openid)

        return res

    def getOpenidNature(self, openid, nature):
        res = self.sr.hget(openid, nature)

        return jsonify(res)

    def deleteOpenidNature(self, openid, keys):
        res = self.sr.hdel(openid, keys)

        return res

class Mysqluse(object):
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='jws',
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    def exec(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(str(e))

    def insertStudentMessage(self, data):
        sql_str = "INSERT INTO student(studennt_id,password,major,openid,binding_time,img) VALUE('{student_id}','{password}','{major}','{openid}','{binding_time}','{nickname}','{img}','{email}','{college}')".format(student_id=data['student_id'], password=data['password'], major=data['major'], openid=data['openid'], binding_time=data['binding_time'], nickname=data['nickname'], img=data['img'], email=data['email'], college=data['college'])
        result = self.exec(sql_str)
        return result

    # def updateStudentMessage(self, data):
    #     sql_str = "UPDATE student SET"



