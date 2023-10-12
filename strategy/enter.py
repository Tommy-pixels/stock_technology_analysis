# -*- encoding: UTF-8 -*-
import numpy
import talib as tl
import pandas as pd
import logging


# TODO 真实波动幅度（ATR）放大
# 最后一个交易日收市价从下向上突破指定区间内最高价
def check_breakthrough(code_name, data, end_date=None, threshold=30):
    max_price = 0
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold+1)
    if len(data) < threshold + 1:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 最后一天收市价
    last_close = float(data.iloc[-1]['收盘'])
    last_open = float(data.iloc[-1]['开盘'])

    data = data.head(n=threshold)
    second_last_close = data.iloc[-1]['收盘']

    for index, row in data.iterrows():
        if row['收盘'] > max_price:
            max_price = float(row['收盘'])

    if last_close > max_price > second_last_close and max_price > last_open \
            and last_close / last_open > 1.06:
        return True
    else:
        return False


# 收盘价高于N日均线
def check_ma(code_name, data, end_date=None, ma_days=250):
    if data is None or len(data) < ma_days:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, ma_days))
        return False

    ma_tag = 'ma' + str(ma_days)
    data[ma_tag] = pd.Series(tl.MA(data['收盘'].values, ma_days), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    last_close = data.iloc[-1]['收盘']
    last_ma = data.iloc[-1][ma_tag]
    if last_close > last_ma:
        return True
    else:
        return False


# 上市日小于60天
def check_new(code_name, data, end_date=None, threshold=60):
    size = len(data.index)
    if size < threshold:
        return True
    else:
        return False


# 量比大于2
# 例如：
#   2017-09-26 2019-02-11 京东方A
#   2019-03-22 浙江龙盛
#   2019-02-13 汇顶科技
#   2019-01-29 新城控股
#   2017-11-16 保利地产
def check_volume(code_name, data, end_date=None, threshold=60):
    """放量上涨"""
    if len(data) < threshold:
        logging.debug("{0}:样本小于250天...\n".format(code_name))
        return False
    data['vol_ma5'] = pd.Series(tl.MA(numpy.array(list(map(float, data['成交量'].values))), 5), index=data.index.values)

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    if data.empty:
        return False
    p_change = data.iloc[-1]['p_change']
    if p_change < 2 \
            or data.iloc[-1]['收盘'] < data.iloc[-1]['开盘']:
        return False
    data = data.tail(n=threshold + 1)
    if len(data) < threshold + 1:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['收盘']
    # 最后一天成交量
    last_vol = data.iloc[-1]['成交量']

    amount = last_close * last_vol * 100

    # 成交额不低于2亿
    if amount < 200000000:
        return False

    data = data.head(n=threshold)

    mean_vol = data.iloc[-1]['vol_ma5']

    vol_ratio = last_vol / mean_vol
    if vol_ratio >= 2:
        msg = "*{0}\n量比：{1:.2f}\t涨幅：{2}%\n".format(code_name, vol_ratio, p_change)
        logging.debug(msg)
        return True
    else:
        return False


# 量比大于3.0
def check_continuous_volume(code_name, data, end_date=None, threshold=60, window_size=3):
    stock = code_name[0]
    name = code_name[1]
    data['vol_ma5'] = pd.Series(tl.MA(data['成交量'].values, 5), index=data.index.values)
    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold + window_size)
    if len(data) < threshold + window_size:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold+window_size))
        return False

    # 最后一天收盘价
    last_close = data.iloc[-1]['收盘']
    # 最后一天成交量
    last_vol = data.iloc[-1]['成交量']

    data_front = data.head(n=threshold)
    data_end = data.tail(n=window_size)

    mean_vol = data_front.iloc[-1]['vol_ma5']

    for index, row in data_end.iterrows():
        if float(row['成交量']) / mean_vol < 3.0:
            return False

    msg = "*{0} 量比：{1:.2f}\n\t收盘价：{2}\n".format(code_name, last_vol/mean_vol, last_close)
    logging.debug(msg)
    return True


if __name__ == '__main__':
    import time
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
    strategy = '放量上涨'
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
            if(data is not None and not data.empty):
                break
        if(data is None):
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
        if (check_volume(code_name=_, data=data, end_date=end_date, threshold=60)):
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