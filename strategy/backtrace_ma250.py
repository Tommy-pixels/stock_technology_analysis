# -*- encoding: UTF-8 -*-
import talib as tl
import pandas as pd
import logging
from datetime import datetime, timedelta
import time


# 使用示例：result = backtrace_ma250.check(code_name, data, end_date=end_date)
# 如：当end_date='2019-02-01'，输出选股结果如下：
# [('601616', '广电电气'), ('002243', '通产丽星'), ('000070', '特发信息'), ('300632', '光莆股份'), ('601700', '风范股份'), ('002017', '东信和平'), ('600775', '南京熊猫'), ('300265', '通光线缆'), ('600677', '航天通信'), ('600776', '东方通信')]
# 当然，该函数中的参数可能存在过拟合的问题


def check(code_name, data, end_date=None, threshold=60):
    """回踩年线策略
    """
    # 1 检查数据表是否满足基本条件
    if(data is None or len(data) < 250):
        logging.debug("{0}:样本小于250天...\n".format(code_name))
        return
    begin_date = data.iloc[0]['日期']
    if (end_date is not None):
        if (end_date < begin_date):  # 该股票在end_date时还未上市
            logging.debug("{}在{}时还未上市".format(code_name, end_date))
            return False

    # 2 计算250日均线数据
    data['ma250'] = pd.Series(tl.MA(data['收盘'].values, 250), index=data.index.values)

    # 3 过滤数据-保留所需数据
    # 3.1 获取到指定日期为止的数据
    if(end_date is not None):
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    # 3.2 获取最近 threshold 日的数据
    data = data.tail(n=threshold)

    # 4 策略判断——判断回踩年线:
    # 4.1 基本数据
    last_close = data.iloc[-1]['收盘']
    lowest_row = data.iloc[-1]  # 区间最低点
    highest_row = data.iloc[-1]     # 区间最高点
    recent_lowest_row = data.iloc[-1]   # 近期低点

    # 4.2 计算区间最高、最低价格
    for index, row in data.iterrows():
        if(row['收盘'] > highest_row['收盘']):
            highest_row = row
        elif(row['收盘'] < lowest_row['收盘']):
            lowest_row = row

    if(lowest_row['成交量'] == 0 or highest_row['成交量'] == 0):
        return False

    data_front = data.loc[(data['日期'] < highest_row['日期'])]
    data_end = data.loc[(data['日期'] >= highest_row['日期'])]

    if(data_front.empty):
        return False
    # 前半段由年线以下向上突破
    if(not (data_front.iloc[0]['收盘'] < data_front.iloc[0]['ma250'] and data_front.iloc[-1]['收盘'] > data_front.iloc[-1]['ma250'])):
        return False

    if(not data_end.empty):
        # 后半段必须在年线以上运行（回踩年线）
        for index, row in data_end.iterrows():
            if(row['收盘'] < row['ma250']):
                return False
            if(row['收盘'] < recent_lowest_row['收盘']):
                recent_lowest_row = row

    date_diff = datetime.date(datetime.strptime(recent_lowest_row['日期'], '%Y-%m-%d')) - \
                datetime.date(datetime.strptime(highest_row['日期'], '%Y-%m-%d'))

    if(not(timedelta(days=10) <= date_diff <= timedelta(days=50))):
        return False
    # 回踩伴随缩量
    vol_ratio = highest_row['成交量']/recent_lowest_row['成交量']
    back_ratio = recent_lowest_row['收盘'] / highest_row['收盘']

    if(not (vol_ratio > 2 and back_ratio < 0.8)):
        return False
    return True


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock
    from database.base import Tb_Stock_Info
    stock_info_inst = Tb_Stock_Info()
    stock_instance = Stock()
    # stocks = stock_instance.all_stock_lis()
    cursor = stock_info_inst.get_cursor()
    stocks = stock_info_inst.filter_stock_info(cursor=cursor, belong_lis=['沪市A股', '深市A股'])
    end_date = '20231010'
    for _ in stocks:
        stock_code = _[0]
        stock_name = _[1]
        if (stock_code.startswith('3') or stock_code.startswith('688') or stock_code.startswith('8')):
            continue
        print('当前：', _)
        data = stock_instance.single_stock_data(stock=_, start_date='20220501')
        if (check(code_name=_, data=data, end_date=end_date, threshold=60)):
            print('满足回踩年线策略：{}'.format(_))
        time.sleep(2)
