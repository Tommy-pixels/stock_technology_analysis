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
    from database.log import Tb_Log
    from database.tb_matched_stock import Tb_Matched_Stock
    from utils.common import Control_Time

    stock_info_inst = Tb_Stock_Info()
    stock_instance = Stock()
    # stocks = stock_instance.all_stock_lis()
    cursor = stock_info_inst.get_cursor()
    stocks = stock_info_inst.filter_stock_info(
        cursor=cursor, belong_lis=['沪市A股', '深市A股']
    )
    cursor.close()
    start_date = '2022-05-01'
    end_date = '2023-10-10'
    strategy = '回踩年线'
    action_name = '策略选股-' + strategy
    operation_id = Tb_Log.generate_operation_id(name=action_name)
    cursor = Tb_Log.get_cursor()
    for _ in stocks:
        stock_code = _[0]
        stock_name = _[1]
        print('当前：', _)
        for i in range(3):
            try:
                data = stock_instance.single_stock_data(stock=_, start_date=start_date.replace('-', ''))
            except Exception as e:
                print('请求股票数据接口异常，等待10s重新请求')
                time.sleep(10)
                data = stock_instance.single_stock_data(stock=_, start_date=start_date.replace('-', ''))
            if (data is not None and not data.empty):
                break
        if (data is None):
            print('请求股票数据响应异常：{},跳过'.format(_))
            Tb_Log.create_log(
                cursor=cursor,
                operation_id=operation_id,
                action=action_name,
                action_detail=_[0] + _[1],
                action_status='请求股票数据响应异常',
                create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
                stock=_,
            )
            continue
        # 数据日期过滤
        if (end_date):
            mask = (data['日期'] <= end_date)
            data = data.loc[mask]
        if (check(code_name=_, data=data, end_date=end_date, threshold=60)):
            print('满足{}策略：{}'.format(strategy, _))
            base_data_start_date = data.iloc[0]['日期']
            base_data_end_date = data.iloc[len(data) - 1]['日期']
            action_status = '满足策略'
            Tb_Log.create_log(
                cursor=cursor,
                operation_id=operation_id,
                action=action_name,
                action_detail=_[0] + _[1],
                action_status=action_status,
                create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
                stock=_,
                trace_start_date=data.iloc[0]['日期'],
                trace_end_date=data.iloc[len(data) - 1]['日期']
            )
            # 添加到选股表
            Tb_Matched_Stock.add_matched_stock(
                cursor=cursor,
                operation_id=operation_id,
                matched_strategy=strategy,
                matched_stock=_,
                base_data_type='daily',
                base_data_start_date=base_data_start_date,
                base_data_end_date=base_data_end_date,
                base_data_detail={
                    'start_date': base_data_start_date,
                    'end_date': base_data_end_date,
                },
                backtrace_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
                stock=_,
                note=''
            )
        time.sleep(2)
    cursor.close()
    del cursor
