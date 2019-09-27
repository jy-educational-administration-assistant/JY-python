import pymysql
from include_file.database import HostAccount


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
        sql_str = "INSERT INTO student(account, password, major, openid, binding_time, nickname, img, email, college, full_name, classroom,all_point,major_number) VALUES('{account}','{password}',{major},'{openid}','{binding_time}','{nickname}','{img}',{email},{college},{full_name},{classroom},{all_point},{major_number})".format(account=data['account'], password=data['password'], major=data['major'], openid=data['openid'], binding_time=data['binding_time'], nickname=data['nickname'], img=data['img'], email=data['email'], college=data['college'], full_name=data['full_name'], classroom=data['classroom'], all_point=data['all_point'], major_number=data['major'])
        result = self.exec(sql_str)

        return result

    def updateStudentMessage(self, query_title, query_object, modify_title, modify_object):
        sql_str = "UPDATE student SET `{modify_title}` = '{modify_object}' WHERE `{query_title}` = '{query_object}'".format(modify_title=modify_title, modify_object=modify_object, query_title=query_title,query_object=query_object)
        res = self.exec(sql_str)

        return res

    def untyingStudent(self, query_title, query_object):
        sql_str = "UPDATE student SET `account` = NULL ,`password` = NULL ,`college` = NULL ,`major` = NULL ,`full_name` = NULL ,`classroom` = NULL ,`all_point` = NULL ,`major_number` = NULL WHERE `{query_title}` = '{query_object}'".format(query_title=query_title,query_object=query_object)
        res = self.exec(sql_str)

        return res

    def selectStudentMessage(self, query_title, query_object):
        sql_str = "SELECT * FROM student WHERE `{query_title}` = '{query_object}'".format(query_title=query_title, query_object=query_object,)
        res = self.query(sql_str)

        return res

    def sclectAllStudent(self):
        sql_str = "SELECT * FROM student"
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
            sql_str = "INSERT INTO grade(account,term,year,code,lesson_name,type,credit,point,usual_score,term_end_score,make_up_score,rebuild_score,all_score,teach_college)VALUES('{account}','{term}','{year}','{code}','{lesson_name}','{type}','{credit}','{point}','{usual_score}','{term_end_score}','{make_up_score}','{rebuild_score}','{all_score}','{teach_college}')".format(account=account, year=year, term=term, code=data['lesson_code'], lesson_name=data['lesson_name'], credit=data['credit'], point=data['point'], all_score=data['all_score'], usual_score=str(data['peace_score']), term_end_score=str(data['term_end_score']), type=data['lesson_nature'], make_up_score=data['bkcj'], rebuild_score=data['cxcj'], teach_college=data['teach_college'])
            self.cur.execute('SET character_set_connection=utf8;')
            res = self.exec(sql_str)
            return res

    def selectScore(self,  account, data):
        if data['term'] is None and data['year'] is None:
            sql_str = "SELECT * FROM grade WHERE `account` = '{account}' ORDER BY year DESC ".format(account=account)
        else:
            if data['term'] is None:
                sql_str = "SELECT * FROM grade WHERE `account` = '{account}' AND `year` = '{year}' ORDER BY year DESC ".format(year=data['year'], account=account)
            elif data['year'] is None:
                sql_str = "SELECT * FROM grade WHERE  `account` = '{account}' AND  `term` ='{term}' ORDER BY year DESC ".format(term=data['term'], account=account)
            else:
                sql_str = "SELECT * FROM grade WHERE `account` = '{account}'AND `term` = '{term}' AND `year` = '{year}'ORDER BY year DESC ".format(year=data['year'], term=data['term'], account=account)
        res = self.query(sql_str)
        return res

    def putSqlWhereField(self, data):
        sql_where = ''
        for title in data:
            sql = "`{title}` = '{res_data}' AND ".format(title=title, res_data=data[title])
            sql_where = sql_where + sql
        sql_where = sql_where[:-4]

        return sql_where

    def putSqlSetField(self, data):
        sql_where = ''
        for title in data:
            sql = "`{title}` = '{res_data}', ".format(title=title, res_data=data[title])
            sql_where = sql_where + sql
        sql_where = sql_where[:-2]

        return sql_where

    def validateScore(self, data):
        sql_where = self.putSqlWhereField(data)
        sql_table = "SELECT * FROM grade WHERE "
        sql_str = sql_table + sql_where + ' ORDER BY year, term, code'
        res = self.query(sql_str)

        return res

    def updateDateScore(self, query_obj, data):
        sql_str_set = self.putSqlSetField(data)
        sql_str_where = self.putSqlWhereField(query_obj)
        sql_str = "UPDATE grade SET " + sql_str_set + " WHERE " + sql_str_where
        res = self.exec(sql_str)
        return res

    def putSqlInsert(self, data):
        sql_table_field = ''
        sql_table_value = ''
        for title in data:
            sql = "'{res_data}', ".format(res_data=data[title])
            sql_filed = "{title},".format(title=title)
            sql_table_field = sql_table_field + sql_filed
            sql_table_value = sql_table_value + sql
        sql_table_field = sql_table_field[:-1]
        sql_table_value = sql_table_value[:-2]

        return {'field': sql_table_field, 'value': sql_table_value}

    def insertNewScore(self, data):
        field_data = self.putSqlInsert(data)
        sql_table = "INSERT INTO grade("
        sql_values = ")VALUES("
        sql_str = sql_table + field_data['field'] + sql_values + field_data['value'] + ")"
        res = self.exec(sql_str)

        return res

    def insertSchedule(self, year, term, day, lesson, classroom, data):
        sql_str = "INSERT INTO course(course_name,place,class_week,teacher,classroom,day,lesson,school_year,term,color,time,section,weeks_arr)VALUES('{course_name}','{place}','{class_week}','{teacher}','{classroom}','{day}','{lesson}','{school_year}','{term}','{color}','{time}','{section}','{weeks_arr}')".format(course_name=data['name'], place=data['place'], classroom=classroom, class_week=data['weeks_text'], teacher=data['teacher'], day=day, lesson=lesson, school_year=year, term=term, color=data['color'], time=data['time'], section=data['section'], weeks_arr=''.join(str(data['weeks_arr'])))
        res = self.exec(sql_str)

        return res

    def selectSchedule(self, classroom, year, term):
        sql_str = "SELECT * FROM course WHERE `school_year` = '{year}' AND `term` = '{term}' AND  `classroom` = '{classroom}'".format(year=year, term=term, classroom=classroom)
        res = self.query(sql_str)
        return res

    def validateSchedule(self, data):
        sql_where = self.putSqlWhereField(data)
        sql_table = "SELECT * FROM course WHERE "
        sql_str = sql_table + sql_where
        res = self.query(sql_str)

        return res
