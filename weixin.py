import urllib.request
import urllib.parse
# from flask import Flask, request, redirect, jsonify
from school_api import SchoolClient
import json
from redis import StrictRedis
import pymysql
#如果上传到服务器，注释sys,path.append
import sys
sys.path.append('D:\枼玉清的文档\python\jws')
from database import HostAccount


school = SchoolClient('http://jws.hebiace.edu.cn/default2.aspx')
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

    def getHostName(self):
        database = HostAccount()
        data = database.getHostNature()

        return data


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

        return res

    def getOpenidNatureAll(self, openid):
        res = self.sr.hgetall(openid)

        return res

    def deleteOpenidNature(self, openid, keys):
        res = self.sr.hdel(openid, keys)

        return res


class MysqlUse(object):
    def __init__(self):
        database = HostAccount()
        data = database.getHostNature()
        self.conn = pymysql.connect(
            host=data['host'],
            user=data['user'],
            password=data['password'],
            database=data['database'],
            charset='utf8',
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    def configMysql(self):
        msg = "链接成功"
        return True

    def query(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def exec(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(str(e))

    def insertStudentMessage(self, data):
        sql_str = "INSERT INTO student(student_id, password, major, openid, binding_time, nickname, img, email, college, full_name, classroom) VALUES('{student_id}','{password}','{major}','{openid}','{binding_time}','{nickname}','{img}','{email}','{college}','{full_name}','{classroom}')".format(student_id=data['student_id'], password=data['password'], major=data['major'], openid=data['openid'], binding_time=data['binding_time'], nickname=data['nickname'], img=data['img'], email=data['email'], college=data['college'], full_name=data['full_name'], classroom=data['classroom'])
        result = self.exec(sql_str)

        return result

    def updateStudentMessage(self, query_title, query_object, modify_title, modify_object):
        sql_str = "UPDATE student SET `{modify_title}` = '{modify_object}' WHERE `{query_title}` = '{query_object}'".format(modify_title=modify_title, modify_object=modify_object, query_title=query_title,query_object=query_object)
        res = self.exec(sql_str)

        return res

    def deleteStudentMessage(self, student_id):
        sql_str = "DELETE FROM student WHERE  `student_id` = '{student_id}'".format(student_id=student_id)
        res = self.exec(sql_str)

        return res

    def selectStudentMessage(self, query_title, query_object):
        sql_str = "SELECT * FROM student WHERE `{query_title}` = '{query_object}'".format(query_title=query_title, query_object=query_object,)
        res = self.query(sql_str)

        return res

    def insertAdmin(self, data):
        sql_str = "INSERT INTO admin(admin_name, admin_password,time) VALUES('{admin_name}','{admin_password}','{time}')".format(admin_name=data['admin_name'], admin_password=data['admin_password'], time=data['time'])
        res = self.exec(sql_str)

        return res

    def insertStudentOther(self, query_object, data):
        sql_str = "UPDATE student SET `major` = '{major}',`college` = '{college}',`full_name`='{full_name}',`classroom`='{classroom}'  WHERE `openid` = '{query_object}'".format(major=data['student_zy'], college=data['student_xy'], full_name=data['student_name'], classroom=data['student_xzb'], query_object=query_object)
        self.cur.execute('SET character_set_connection=utf8;')
        res = self.exec(sql_str)

        return res




