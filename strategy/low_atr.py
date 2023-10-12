# -*- encoding: UTF-8 -*-
import pandas as pd
import talib as tl
import logging


# 低ATR成长策略
def check_low_increase(code_name, data, end_date=None, ma_short=30, ma_long=250, threshold=10):
    stock = code_name[0]
    name = code_name[1]
    if len(data) < ma_long:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, ma_long))
        return False

    data['ma_short'] = pd.Series(tl.MA(data['收盘'].values, ma_short), index=data.index.values)
    data['ma_long'] = pd.Series(tl.MA(data['收盘'].values, ma_long), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold)
    inc_days = 0
    dec_days = 0
    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 区间最低点
    lowest_row = data.iloc[-1]
    # 区间最高点
    highest_row = data.iloc[-1]

    days_count = len(data)
    total_change = 0.0
    for index, row in data.iterrows():
        if 'p_change' in row:
            p_change = float(row['p_change'])
            if abs(p_change) > 0:
                total_change += abs(p_change)
            # if p_change < -7:
            #     return False
            # if row['ma_short'] < row['ma_long']:
            #     return False

            if p_change > 0:
                inc_days = inc_days + 1
            if p_change < 0:
                dec_days = dec_days + 1

            if row['收盘'] > highest_row['收盘']:
                highest_row = row
            if row['收盘'] < lowest_row['收盘']:
                lowest_row = row

    atr = total_change / days_count
    if atr > 10:
        return False

    ratio = (highest_row['收盘'] - lowest_row['收盘']) / lowest_row['收盘']

    if ratio > 1.1:
        logging.debug("股票：{0}（{1}）  最低:{2}, 最高:{3}, 涨跌比率:{4}       上涨天数:{5}， 下跌天数:{6}".format(name, stock, lowest_row['日期'], highest_row['日期'], ratio, inc_days, dec_days))
        return True
    return False


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock
    from database.base import Tb_Stock_Info
    from database.log import Tb_Log
    from database.tb_matched_stock import Tb_Matched_Stock
    from utils.common import Control_Time
    import time

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
    strategy = '低ATR成长'
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
        if (check_low_increase(code_name=_, data=data, end_date=end_date, threshold=10)):
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
