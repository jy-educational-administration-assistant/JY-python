from include_file.schoolapiget import SchoolApiGet
from include_file.sqluse import MysqlUse


class UseApply(object):
    def getScore(self, account, password, score_year='', score_term='',):
        db = MysqlUse()
        sch = SchoolApiGet()
        # i = ''
        school_data = sch.get_score_info(account, password, score_year, score_term)
        res_allcollege_1 = db.updateStudentMessage('account', account, 'all_point', school_data['all_college']['pjzjd'])
        if not res_allcollege_1:
            return False
        res_allcollege_2 = db.updateStudentMessage('account', account, 'major_number', school_data['all_college']['zyzrs'])
        if not res_allcollege_2:
            return False
        for key_year, value in school_data['score_info'].items():
            for key_term, value_data in value.items():
                for res in value_data:
                    sql_res = db.insertScore(key_year, key_term, res, account)
                    # i = i + sql_res
                    if not sql_res:
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
                'account': data[x][0],
                'term': data[x][1],
                'year': data[x][2],
                'code': data[x][3],
                'lesson_name': data[x][4],
                'type': data[x][5],
                'credit': data[x][6],
                'point': data[x][7],
                'usual_score': data[x][8],
                'term_end_score': data[x][9],
                'make_up_score': data[x][10],
                'rebuild_score': data[x][11],
                'all_score': data[x][12],
                'teach_college': data[x][13],
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
