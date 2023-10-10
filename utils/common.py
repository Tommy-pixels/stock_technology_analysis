# -*- coding: UTF-8 -*-
import datetime
import base64
from urllib import parse
import hashlib
import time


class Encode:
    """
        加密相关的基类和方法
    """
    # 统一输出类型为str
    @staticmethod
    def bytes2str(b):
        return str(b, encoding='utf-8')

    @staticmethod
    def str2bytes(s):
        return bytes(s, encoding='utf-8')

    @staticmethod
    def encodeByMd5(s):
        return hashlib.md5(s.encode(encoding='utf-8')).hexdigest()

    # base64输出的为bytes类型 要转化为字符串
    @classmethod
    def encodeByBase64(cls, s):
        res = base64.encodebytes(bytes(s, encoding='utf-8')).strip()
        # 转换为字符串
        res = cls.bytes2str(res)
        return res

    @staticmethod
    def encodeBySHA1(s):
        if(not isinstance(s, bytes)):
            text = bytes(s, 'utf-8')
        sha = hashlib.sha1(text)
        encrypts = sha.hexdigest()
        return encrypts

    @classmethod
    def encode0(cls, s):
        return cls.encodeByBase64(cls.str2bytes(cls.encodeByMd5(s)))

    @staticmethod
    def str2urlcode(s):
        '''
        将字符串转换为浏览器url编码格式
        '''
        return parse.quote(s)

    @staticmethod
    def urlcode2str(urlcode):
        '''
        将url编码转换为字符串格式
        '''
        return parse.unquote(urlcode)

    @staticmethod
    def parse_decode(resp_content:bytes, encoding_type_lis=['utf-8', 'gbk', 'gb2312']):
        """处理请求返回结果 解码输出字符串格式
        :param resp_content 请求返回的bytes类型 res.content
        :param encoding_type_lis 潜在编码类型列表
        :output resp_text 转码结果 字符串格式
        """
        resp_text = ''
        for encoding_type in encoding_type_lis:
            try:
                resp_text = resp_content.decode(encoding_type)
            except Exception as e:
                print('编码格式 {} 解码失败'.format(encoding_type))
                continue
            print('编码格式 {} 解码成功'.format(encoding_type))
            break
        return resp_text


class Control_Time:
    """时间（时间戳、日期、年月日等）处理相关的基类和方法"""
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

    @staticmethod
    def get_millisecond():
        '''返回毫秒级时间戳'''
        return int(round(time.time() * 1000))

    # 获取当前日期
    @staticmethod
    def get_cur_date(formatStr: str):
        '''
        获取当前日期
        :param formatStr: 指定格式 如 "%Y%m%d"
        :return:
        '''
        return time.strftime(formatStr, time.localtime())

    @staticmethod
    def get_timestamp_by_date(date, format='%Y-%m-%d %H:%M:%S'):
        """返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00"""
        b = time.strptime(date, format)
        return time.mktime(b)

    @classmethod
    def get_recent_date(cls, days=1, time_format='%Y-%m-%d', date_start='', mode='before'):
        """获取离当前日期往前推最近的n天的日期
        :param date_start 开始的计算日期
        :param mode 推算的模式 after 往后推
        """
        dic = {
            'recent_date_lis': [],
            'time_format': time_format
        }
        if (not date_start):
            date_start = datetime.datetime.now()
        if (date_start and type(date_start) == str):
            date_start = datetime.datetime.strptime(date_start, time_format)
        if (mode == 'after'):
            for i in range(0, days + 1):
                day = date_start + datetime.timedelta(days=i)
                date_to = str(day.year) + '-' + str(day.month) + '-' + str(day.day)
                dic['recent_date_lis'].append(date_to)
        else:
            for i in range(0, days + 1):
                day = date_start - datetime.timedelta(days=i)
                date_to = str(day.year) + '-' + str(day.month) + '-' + str(day.day)
                dic['recent_date_lis'].append(date_to)
        return dic


if __name__ == '__main__':
    print(Control_Time.between_n_days(date='2023-10-01', n_days=10))
