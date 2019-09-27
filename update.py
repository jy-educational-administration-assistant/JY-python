#!/usr/bin/python3
# -*-coding:utf-8 -*-
# Reference:**********************************************
# @Time    : 2019/9/24 21:08
# @Author  : yeyuqing
# @File    : update.py
# @Software: PyCharm
# Reference:**********************************************

from include_file.sqluse import MysqlUse
from include_file.user import UseApply


def updateInfromation():
    db = MysqlUse()
    use = UseApply()
    num_all = db.sclectAllStudent()
    for even in num_all:
        res_score = use.updateScoreInformation(even[1], even[2])
        if 'error' in res_score:
            print({'code': 1, 'msg': res_score, 'id': even[0]})
        else:
            print({'code': 0, 'data': res_score, 'id': even[0]})
        res_schedule = use.updateScheduleInformation(even[1], even[2], even[8])
        if 'error' in res_schedule:
            print({'code': 1, 'msg': res_schedule, 'classroom': even[8]})
        else:
            print({'code': 0, 'data': res_schedule, 'classroom': even[8]})


if __name__ == '__main__':
        updateInfromation()
