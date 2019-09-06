import json
import pymysql
import urllib.parse
import urllib.request
from redis import Redis
from redis import StrictRedis
from school_api import SchoolClient
#如果上传到服务器，注释sys,path.append
import sys
sys.path.append('D:\枼玉清的文档\python\jws')
from database import HostAccount
from school_api.session.redisstorage import RedisStorage

redis = Redis()
session = RedisStorage(redis)
conf = {
    "url": 'http://jws.hebiace.edu.cn/default2.aspx',
    "session": session,
    'name': '河北建筑工程学院',
    'code': 'hbjg'
}

school = SchoolClient(**conf)

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
        res_time = self.sr.expire(openid, 604800)

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
        sql_str = "INSERT INTO student(student_id, password, major, openid, binding_time, nickname, img, email, college, full_name, classroom,all_point,major_number) VALUES('{student_id}','{password}','{major}','{openid}','{binding_time}','{nickname}','{img}','{email}','{college}','{full_name}','{classroom}','{all_point}','{major_number}')".format(student_id=data['student_id'], password=data['password'], major=data['major'], openid=data['openid'], binding_time=data['binding_time'], nickname=data['nickname'], img=data['img'], email=data['email'], college=data['college'], full_name=data['full_name'], classroom=data['classroom'], all_point=data['all_point'], major_number=data['major'])
        result = self.exec(sql_str)

        return result

    def updateStudentMessage(self, query_title, query_object, modify_title, modify_object):
        sql_str = "UPDATE student SET `{modify_title}` = '{modify_object}' WHERE `{query_title}` = '{query_object}'".format(modify_title=modify_title, modify_object=modify_object, query_title=query_title,query_object=query_object)
        res = self.exec(sql_str)

        return sql_str

    def untyingStudent(self, query_title, query_object):
        sql_str = "UPDATE student SET `student_id` = NULL ,`password` = NULL ,`college` = NULL ,`major` = NULL ,`full_name` = NULL ,`classroom` = NULL ,`all_point` = NULL ,`major_number` = NULL WHERE `{query_title}` = '{query_object}'".format(query_title=query_title,query_object=query_object)
        res = self.exec(sql_str)

        return res


    def deleteStudentMessage(self, student_id):
        sql_str = "DELETE FROM score WHERE  `student_id` = '{student_id}'".format(student_id=student_id)
        res = self.exec(sql_str)

        return res

    def selectStudentMessage(self, query_title, query_object):
        sql_str = "SELECT * FROM student WHERE `{query_title}` = '{query_object}'".format(query_title=query_title, query_object=query_object,)
        res = self.query(sql_str)

        return res

    def insertAdmin(self, data):
        sql_str = "INSERT INTO admin(admin_name,admin_password,time) VALUES('{admin_name}','{admin_password}','{time}')".format(admin_name=data['admin_name'], admin_password=data['admin_password'], time=data['time'])
        res = self.exec(sql_str)

        return res

    def insertStudentOther(self, query_object, data):
        sql_str = "UPDATE student SET `major` = '{major}',`college` = '{college}',`full_name`='{full_name}',`classroom`='{classroom}'  WHERE `openid` = '{query_object}'".format(major=data['student_zy'], college=data['student_xy'], full_name=data['student_name'], classroom=data['student_xzb'], query_object=query_object)
        self.cur.execute('SET character_set_connection=utf8;')
        res = self.exec(sql_str)

        return res

    def insertScore(self, year, term, data, account):
            if 'bkcj' not in data.keys():
                data['bkcj'] = '0'
            if 'cxcj' not in data.keys():
                    data['cxcj'] = '0'
            sql_str = "INSERT INTO grade(term,school_year,course_code,course_name,credit,point,score,nature,student_id,usual_score,makeup_score,term_score,rebuild_score,college)VALUES('{term}','{school_year}','{course_code}','{course_name}','{credit}','{point}','{score}','{nature}','{student_id}','{usual_score}','{makeup_score}','{term_score}','{rebuild_score}','{college}')".format(term=term, school_year=year, course_code=data['lesson_code'], course_name=data['lesson_name'], credit=data['credit'], point=data['point'], score=data['all_score'], usual_score=data['peace_score'], term_score=data['term_end_score'], nature=data['lesson_nature'], student_id=account, makeup_score=data['bkcj'], rebuild_score=data['cxcj'], college=data['teach_college'])
            self.cur.execute('SET character_set_connection=utf8;')
            res = self.exec(sql_str)
            return res

    def selectScore(self,  account, data):
        if data['term'] is None and data['year'] is None:
            sql_str = "SELECT * FROM grade WHERE `student_id` = '{account}'".format(account=account)
        else:
            if data['term'] is None:
                sql_str = "SELECT * FROM grade WHERE `school_year` = '{year}' AND  `student_id` = '{account}'".format(year=data['year'], account=account)
            elif data['year'] is None:
                sql_str = "SELECT * FROM grade WHERE  `term` = '{term}' AND  `student_id` = '{account}'".format(term=data['term'], account=account)
            else:
                sql_str = "SELECT * FROM grade WHERE `school_year` = '{year}' AND `term` = '{term}' AND  `student_id` = '{account}'".format(year=data['year'], term=data['term'], account=account)
        res = self.query(sql_str)
        return res

    def insertSchedule(self, year, term, day, lesson, classroom, data):
        sql_str = "INSERT INTO course(course_name,place,class_week,teacher,classroom,day,lesson,school_year,term,color,time,section)VALUES('{course_name}','{place}','{class_week}','{teacher}','{classroom}','{day}','{lesson}','{school_year}','{term}','{color}','{time}','{section}')".format(course_name=data['name'], place=data['place'], classroom=classroom, class_week=data['weeks_text'], teacher=data['teacher'], day=day, lesson=lesson, school_year=year, term=term, color=data['color'], time=data['time'], section=data['section'])
        res = self.exec(sql_str)

        return res

    def selectSchedule(self, classroom, year, term):
        sql_str = "SELECT * FROM course WHERE `school_year` = '{year}' AND `term` = '{term}' AND  `classroom` = '{classroom}'".format(year=year, term=term, classroom=classroom)
        res = self.query(sql_str)
        return res


class UseApply(object):
    def getScore(self, account, password, score_year='', score_term='',):
        db = MysqlUse()
        # i = ''
        user = school.user_login(account, password)
        school_data = user.get_score(score_year, score_term, use_api=3)
        res_allcollege_1 = db.updateStudentMessage('student_id', account, 'all_point', school_data['all_college']['pjzjd'])
        if not res_allcollege_1:
            return False
        res_allcollege_2 = db.updateStudentMessage('student_id', account, 'major_number', school_data['all_college']['zyzrs'])
        if not res_allcollege_2:
            return False
        for key_year, value in school_data['score_info'].items():
            for key_term, value_data in value.items():
                for res in value_data:
                    sql_res = db.insertScore(key_year, key_term, res, account)
                    # i = i + sql_res
                    if sql_res is None:
                        return sql_res
        return True

    def getSchedule(self, account, password, schedule_year, schedule_term, classroom):
        db = MysqlUse()
        sch = SchoolApiGet()
        res_schedule = sch.get_schedule_info(account, password, schedule_year, schedule_term)
        for day in range(len(res_schedule['schedule'])):
            for lesson in range(len(res_schedule['schedule'][day])):
                for x in range(len(res_schedule['schedule'][day][lesson])):
                    res_sql = db.insertSchedule(res_schedule['schedule_year'],  res_schedule['schedule_term'], day, lesson, classroom,  res_schedule['schedule'][day][lesson][x])
                    if not res_sql:
                        return False

        return res_schedule

    def manageScore(self, data):
        res_score = []
        for x in range(len(data)):
            data_res = {
                'term': data[x][0],
                'year': data[x][1],
                'code': data[x][2],
                'name': data[x][3],
                'credit': data[x][4],
                'score': data[x][5],
                'usual_score': data[x][6],
                'makeup_score': data[x][7],
                'term_end_score': data[x][8],
                'rebuild_score': data[x][9],
                'nature': data[x][10],
                'college': data[x][11],
            }
            res_score.append(data_res)

        return res_score

    def mangageSchedule(self,data):
        res_schedule = []
        for x in range(len(data)):
            data_res = {
                'name': data[x][0],
                'place': data[x][1],
                'weeks_text': data[x][2],
                'teacher': data[x][3],
                'classroom': data[x][4],
                'day': data[x][5],
                'lesson': data[x][6],
                'year': data[x][7],
                'term': data[x][8],
                'color': data[x][9],
                'time': data[x][10],
                'section': data[x][11],
            }
            res_schedule.append(data_res)

        return res_schedule


class SchoolApiGet(object):
    def get_student(self, account, password):
        user = school.user_login(account, password)
        for i in 're':
            student_info = user.get_student_info()

        return student_info

    def get_score_info(self, account, password, score_year=0, score_term=0):
        user = school.user_login(account, password)
        school_data = user.get_score(score_year, score_term, use_api=3)

        return school_data

    def validate_user(self, account, password):
        user = school.user_login(account, password, use_cookie_login=False)
        res = hasattr(user, 'tip')
        if res is True:
            data = {
                'code': 1,
                'msg': user.tip
            }
            return data
        else:
            return False

    def get_schedule_info(self, account, password, schedule_year, schedule_term, schedule_type=1):
        user = school.user_login(account, password)
        schedule_data = user.get_schedule(schedule_year, schedule_term, schedule_type)

        return schedule_data
