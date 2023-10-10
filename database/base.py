import pymysql
from utils.common import Control_Time

DATABASE_NAME = 'db_stock_analysis'


class Base_DB:
    @classmethod
    def get_cursor(cls):
        cursor = None
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='db_stock_analysis',
            autocommit=True,
            port=3306,
            charset='utf8'
        )
        cursor = conn.cursor()
        return cursor


class Tb_Stock_Info(Base_DB):
    """ 股票池
    `id` int NOT NULL AUTO_INCREMENT,
    `stock_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `stock_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `belong` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `note` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    """
    def __init__(self):
        __TB_NAME__ = 'tb_stock_info'

    @classmethod
    def add_stock_info(cls, cursor, stock_name, stock_code, belong, **kwargs):
        """插入股票数据"""
        note = kwargs.get('note', '')
        if(not stock_name or not stock_code):
            print('股票名/股票码为空')
            return False
        insert_result = True
        sql_insert = "INSERT INTO tb_stock_info (stock_name, stock_code, belong, note) " \
                     "SELECT '{}', '{}', '{}', '{}' FROM DUAL WHERE NOT EXISTS(" \
                     "SELECT id FROM tb_stock_info WHERE stock_name='{}' AND stock_code='{}' AND belong='{}');".format(
            stock_name, stock_code, belong, note, stock_name, stock_code, belong
        )
        try:
            query_res = cursor.execute(sql_insert)
            insert_result = True
        except Exception as e:
            print('sql执行异常：', sql_insert)
            query_res = -1
        return insert_result

    @classmethod
    def filter_stock_info(cls, cursor, belong_lis=[], **kwargs):
        """股票查询"""
        stock_lis = []
        where_condition = ''
        if(belong_lis):
            _or_part = ''
            for _ in belong_lis:
                _or_part = _or_part + ' OR belong=\'{}\''.format(
                    _
                )
            _or_part = _or_part.lstrip(' OR ')
            where_condition = where_condition + ' AND ' + '({})'.format(_or_part)
        where_condition = where_condition.lstrip(' AND ')
        if(where_condition):
            sql_query = 'SELECT stock_code, stock_name FROM tb_stock_info WHERE {};'.format(
                where_condition
            )
        else:
            sql_query = 'SELECT stock_code, stock_name FROM tb_stock_info;'
        try:
            query_res = cursor.execute(sql_query)
            stock_lis = cursor.fetchall()
        except:
            print('sql执行异常：', sql_query)
            query_res = -1
        return stock_lis


class Tb_Stock_Daily_Data(Base_DB):
    """ 股票日数据
        `id` int NOT NULL AUTO_INCREMENT,
        `stock_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
        `opening_price` decimal(10, 3) NULL DEFAULT NULL,
        `closing_price` decimal(10, 3) NULL DEFAULT NULL,
        `the_highest_price` decimal(10, 3) NULL DEFAULT NULL,
        `the_lowest_price` decimal(10, 3) NULL DEFAULT NULL,
        `date` date NULL DEFAULT NULL,
        `trading_volume` bigint NULL DEFAULT NULL COMMENT '成交量',
        `business_volume` bigint NULL DEFAULT NULL COMMENT '成交额',
        `amplitude` decimal(10, 3) NULL DEFAULT NULL COMMENT '振幅',
        `advance_decline_amplitude` decimal(10, 3) NULL DEFAULT NULL COMMENT '涨跌幅',
        `advance_decline_volume` decimal(10, 3) NULL DEFAULT NULL COMMENT '涨跌额',
        `turnover_rate` decimal(10, 3) NULL DEFAULT NULL COMMENT '换手率',
        `note` longtext NULL DEFAULT NULL ,
    """
    def __init__(self):
        __TB_NAME__ = 'tb_stock_daily_data'

    @classmethod
    def add_stock_info(cls, cursor, stock_code, date, **kwargs):
        """插入股票日数据"""
        opening_price = kwargs.get('opening_price', '')
        closing_price = kwargs.get('closing_price', '')
        the_highest_price = kwargs.get('the_highest_price', '')
        the_lowest_price = kwargs.get('the_lowest_price', '')
        trading_volume = kwargs.get('trading_volume', '')
        business_volume = kwargs.get('business_volume', '')
        amplitude = kwargs.get('amplitude', '')
        advance_decline_amplitude = kwargs.get('advance_decline_amplitude', '')
        advance_decline_volume = kwargs.get('advance_decline_volume', '')
        turnover_rate = kwargs.get('turnover_rate', '')
        note = kwargs.get('note', '')
        if (not stock_code):
            print('股票码为空')
            return False
        result = False
        # 判断日期是在一个月内
        need_update = False
        if(Control_Time.between_n_days(date=date, n_days=-30)):
            # 过去一个月内的数据要更新 更久的不用
            need_update = True
        if(need_update):
            sql_check_id = 'SELECT id FROM tb_stock_daily_data WHERE stock_code=\'{}\' AND date=\'{}\';'.format(
                stock_code, date
            )
            cursor.execute(sql_check_id)
            query_res = cursor.fetchone()
            if(not query_res):
                # 插入
                sql = "INSERT INTO tb_stock_daily_data (" \
                      "stock_code, opening_price, closing_price, the_highest_price, the_lowest_price, date, trading_volume, business_volume, amplitude, advance_decline_amplitude, advance_decline_volume, turnover_rate, note" \
                      ") VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                    stock_code, opening_price, closing_price, the_highest_price, the_lowest_price, date, trading_volume, business_volume, amplitude, advance_decline_amplitude, advance_decline_volume, turnover_rate, note,
                )
                try:
                    query_res = cursor.execute(sql)
                    result = True
                except Exception as e:
                    print('sql执行异常：', sql)
                    query_res = -1
            else:
                # 更新
                record_id = query_res[0]
                sql = "UPDATE tb_stock_daily_data SET " \
                      "closing_price=\'{}\', the_highest_price=\'{}\', the_lowest_price=\'{}\', trading_volume=\'{}\', " \
                      "business_volume=\'{}\', amplitude=\'{}\', advance_decline_amplitude=\'{}\', advance_decline_volume=\'{}\', " \
                      "turnover_rate=\'{}\'" \
                      "WHERE id=\'{}\';".format(
                    closing_price, the_highest_price, the_lowest_price, trading_volume, business_volume, amplitude, advance_decline_amplitude,
                    advance_decline_volume, turnover_rate, record_id
                )
                try:
                    query_res = cursor.execute(sql)
                    result = True
                except Exception as e:
                    print('sql执行异常：', sql)
                    query_res = -1
        else:
            sql = "INSERT INTO tb_stock_daily_data (" \
                         "stock_code, opening_price, closing_price, the_highest_price, the_lowest_price, date, trading_volume, business_volume, amplitude, advance_decline_amplitude, advance_decline_volume, turnover_rate, note) " \
                         "SELECT '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}' FROM DUAL WHERE NOT EXISTS(" \
                         "SELECT id FROM tb_stock_daily_data WHERE stock_code='{}' AND date='{}');".format(
                stock_code, opening_price, closing_price, the_highest_price, the_lowest_price, date, trading_volume, business_volume, amplitude, advance_decline_amplitude, advance_decline_volume, turnover_rate, note,
                stock_code, date
            )
            try:
                query_res = cursor.execute(sql)
                result = True
            except Exception as e:
                print('sql执行异常：', sql)
                query_res = -1
        return result


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock
    stock_info_inst = Tb_Stock_Info()
    stock_daily_data_inst = Tb_Stock_Daily_Data()
    stock_inst = Stock()
    cursor = stock_info_inst.get_cursor()
    stock_lis = stock_info_inst.filter_stock_info(cursor=cursor, belong_lis=['沪市A股', '深市A股'])
    for stock in stock_lis:
        stock_code = stock[0]
        data = stock_inst.single_stock_data(stock=stock)
        total = len(data)
        success_lis = []
        for i in range(total):
            _ = data.iloc[i]
            date = _['日期']
            item_dic = {
                'opening_price': _["开盘"],
                'closing_price': _["收盘"],
                'the_highest_price': _["最高"],
                'the_lowest_price': _["最低"],
                'trading_volume': _["成交量"],
                'business_volume': _["成交额"],
                'amplitude': _["振幅"],
                'advance_decline_amplitude': _["涨跌幅"],
                'advance_decline_volume': _["涨跌额"],
                'turnover_rate': _["换手率"],
                'note': ''
            }
            res = stock_daily_data_inst.add_stock_info(
                cursor=cursor,
                stock_code=stock_code,
                date=date,
                **item_dic
            )
            if(res):
                success_lis.append(item_dic)
        if(len(success_lis) == total):
            print('{} 日数据共 {} 条，录入 {} 条'.format(stock, total, len(success_lis)))
