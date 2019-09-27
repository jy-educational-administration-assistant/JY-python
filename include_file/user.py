from include_file.schoolapiget import SchoolApiGet
from include_file.sqluse import MysqlUse
from dictdiffer import diff


class UseApply(object):
    def getScore(self, account, password, score_year=None, score_term=None,):
        db = MysqlUse()
        sch = SchoolApiGet()
        i = 0
        school_data = sch.get_score_info(account, password, score_year, score_term)
        while 'score_info' not in school_data:
            school_data = sch.get_score_info(account, password, score_year, score_term)
            i = i + 1
            if i >= 4:
                return school_data
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
                        return False
        return True

    def getSchedule(self, account, password, classroom, schedule_year, schedule_term):
        db = MysqlUse()
        i = 0
        sch = SchoolApiGet()
        res_schedule = sch.get_schedule_info(account, password, schedule_year, schedule_term)
        while 'schedule' not in res_schedule:
            res_schedule = sch.get_schedule_info(account, password, schedule_year, schedule_term)
            i = i + 1
            if i >= 4:
                return res_schedule
        for day in range(len(res_schedule['schedule'])):
            for lesson in range(len(res_schedule['schedule'][day])):
                for x in range(len(res_schedule['schedule'][day][lesson])):
                    res_sql = db.insertSchedule(res_schedule['schedule_year'],  res_schedule['schedule_term'], day, lesson, classroom,  res_schedule['schedule'][day][lesson][x])
                    if not res_sql:
                        return False
        return True

    def manageScore(self, data):
        res_score = []
        for x in range(len(data)):
            data_res = {
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

    def mangageSchedule(self, data):
        res_schedule = []
        for x in range(len(data)):
            weeks_arr = data[x][12]
            if weeks_arr:
                weeks_arr = weeks_arr.split('[')
                weeks_arr = weeks_arr[1].split(']')
                weeks_arr = weeks_arr[0].split(',')
            data_res = {
                'name': data[x][0],
                'place': data[x][1],
                'weeks_text': data[x][2],
                'teacher': data[x][3],
                'day': data[x][5],
                'lesson': data[x][6],
                'year': data[x][7],
                'term': data[x][8],
                'bgcolor': data[x][9],
                'time': data[x][10],
                'section': data[x][11],
                'weeks_arr': weeks_arr,
            }
            res_schedule.append(data_res)
        return res_schedule

    def mangageValidateScore(self, data):
        res_score = []
        for x in range(len(data)):
            data_res = {
                'term': str(data[x][1]),
                'year': data[x][2],
                'lesson_code': data[x][3],
                'lesson_name': data[x][4],
                'lesson_nature': data[x][5],
                'credit': data[x][6],
                'point': data[x][7],
                'peace_score': data[x][8],
                'term_end_score': data[x][9],
                'all_score': data[x][12],
                'teach_college': data[x][13],
            }
            if data[x][10]:
                data_res['make_up_score'] = data[x][10]
            elif data[x][11]:
                data_res['rebuild_score'] = data[x][11]
            res_score.append(data_res)

        return res_score

    def updateScoreInformation(self, account, password):
        db = MysqlUse()
        sch = SchoolApiGet()
        query_obj = {}
        data_school = []
        update_score_data = []
        insert_data = []
        l = 0
        school_data = sch.get_score_info(account, password)
        while 'score_info' not in school_data:
            school_data = sch.get_score_info(account, password)
            l += 1
            if l >= 4:
                return school_data
        for key_year, value in school_data['score_info'].items():
            for key_term, value_data in value.items():
                for res in value_data:
                    res['year'] = key_year
                    res['term'] = key_term
                    res['term_end_score'] = str(res['term_end_score'])
                    res['peace_score'] = str(res['peace_score'])
                    data_school.append(res)
        sel_data = {
            'account': account
        }
        res_sql_data = db.validateScore(sel_data)
        res_sql_data = self.mangageValidateScore(res_sql_data)
        if len(res_sql_data) < len(data_school):
            for id_data, k in enumerate(data_school):
                if k not in res_sql_data:
                    insert_data.append(k)
                    if 'bkcj' not in k.keys():
                        k['make_up_score'] = '0'
                    else:
                        k['make_up_score'] = k.pop('bkcj')
                    if 'cxcj' not in k.keys():
                        k['rebuild_score'] = '0'
                    else:
                        k['rebuild_score'] = k.pop('cxcj')
                    k['usual_score'] = k.pop('peace_score')
                    k['account'] = account
                    k['type'] = k.pop('lesson_nature')
                    k['code'] = k.pop('lesson_code')
                    res_insert = db.insertNewScore(k)
                    if not res_insert:
                        return {'error': res_insert}
            res_pjzjd = db.updateStudentMessage('account', account, 'all_point', school_data['all_college']['pjzjd'])
            if not res_pjzjd:
                return {'error': res_pjzjd}
            if insert_data:
                return {'isScore': 0, 'insert': insert_data, 'point': school_data['all_college']['pjzjd']}
            else:
                return {'isScore': 1}
        else:
            for i, j in zip(res_sql_data, data_school):
                different_all = list(diff(j, i))
                if different_all and 'add' not in different_all[0]:
                    for ever_row in different_all:
                        if ever_row[0] is 'change':
                                i[ever_row[1]] = j[ever_row[1]]
                                j['change'] = ever_row
                    i['usual_score'] = i.pop('peace_score')
                    i['type'] = i.pop('lesson_nature')
                    query_obj['code'] = i.pop('lesson_code')
                    query_obj['term'] = i.pop('term')
                    query_obj['year'] = i.pop('year')
                    res_sql = db.updateDateScore(query_obj, i)
                    if not res_sql:
                        return {'error': res_sql}
                    i['code'] = query_obj['code']
                    i['term'] = query_obj['term']
                    i['year'] = query_obj['year']
                    i['change'] = j['change']
                    update_score_data.append(i)
        res_pjzjd = db.updateStudentMessage('account', account, 'all_point', school_data['all_college']['pjzjd'])
        if not res_pjzjd:
            return {'error': res_pjzjd}
        if update_score_data:
            return {'isScore': 0, 'update': update_score_data, 'point': school_data['all_college']['pjzjd']}
        else:
            return {'isScore': 1}

    def updateScheduleInformation(self, account, password, classroom):
        db = MysqlUse()
        sch = SchoolApiGet()
        i = 0
        schedule_data = sch.get_schedule_info(account, password)
        while 'schedule' not in schedule_data:
            res_schedule = sch.get_schedule_info(account, password)
            i = i + 1
            if i >= 4:
                return res_schedule
        if not schedule_data['schedule']:
            return {'isScore': 1}
        sel_schedule = {
            'classroom': classroom,
            'school_year': schedule_data['schedule_year'],
            'term': schedule_data['schedule_term'],
        }
        validate_schedule = db.validateSchedule(sel_schedule)
        if validate_schedule:
            return {'isSchedule': 1}
        else:
            for day in range(len(schedule_data['schedule'])):
                for lesson in range(len(schedule_data['schedule'][day])):
                    for x in range(len(schedule_data['schedule'][day][lesson])):
                        res_sql = db.insertSchedule(schedule_data['schedule_year'], schedule_data['schedule_term'], day,
                                                    lesson, classroom, schedule_data['schedule'][day][lesson][x])
                        if not res_sql:
                            return False
            sel_schedule = {
                'classroom': classroom,
                'school_year': schedule_data['schedule_year'],
                'term': schedule_data['schedule_term'],
            }
            res_select = db.validateSchedule(sel_schedule)
            if not res_select:
                return {'isSchedule': 1}
            else:
                return {'isSchedule': 0}
