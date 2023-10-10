# -*- coding: UTF-8 -*-
import datetime


class Control_Time:
    @classmethod
    def is_weekday(cls):
        # 是否是工作日
        return datetime.datetime.today().weekday() < 5

    @classmethod
    def between_n_days(cls, date, time_format='%Y-%m-%d', n_days:int=-30):
        """判断指定日期是否在指定时间内
        :param n_days 在指定天数内 >0表示在未来n天内     <0表示在过去n天内
        """
        delta_days = (datetime.datetime.strptime(date, time_format) - datetime.datetime.today()).days
        if((delta_days>0 and delta_days<=n_days) or (delta_days<0 and delta_days>=n_days)):
            return True
        else:
            return False


if __name__ == '__main__':
    print(Control_Time.between_n_days(date='2023-10-01', n_days=10))
