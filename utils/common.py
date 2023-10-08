# -*- coding: UTF-8 -*-
import datetime


class Control_Time:
    @classmethod
    def is_weekday(cls):
        # 是否是工作日
        return datetime.datetime.today().weekday() < 5

