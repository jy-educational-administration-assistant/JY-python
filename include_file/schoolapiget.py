from school_api import SchoolClient
from school_api.session.redisstorage import RedisStorage
from redis import Redis

redis = Redis()
session = RedisStorage(redis)
conf = {
    "url": 'http://jws.hebiace.edu.cn/default2.aspx',
    "session": session,
    'name': '河北建筑工程学院',
    'code': 'hbjg'
}

school = SchoolClient(**conf)


class SchoolApiGet(object):

    def get_student(self, account, password):
        i = 0
        user = school.user_login(account, password)
        student_info = user.get_student_info()
        while 'error' in student_info:
            student_info = user.get_student_info()
            i = i + 1
            if i >= 4:
                return student_info
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

    def get_schedule_info(self, account, password, schedule_year=0, schedule_term=0, schedule_type=1):
        user = school.user_login(account, password)
        schedule_data = user.get_schedule(schedule_year, schedule_term, schedule_type)

        return schedule_data
