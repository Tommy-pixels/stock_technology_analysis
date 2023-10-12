# -*- encoding: UTF-8 -*-
import numpy
import talib as tl
import pandas as pd
import logging

# 放量跌停策略
def check(code_name, data, end_date=None, threshold=60):
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
    if p_change > -9.5:
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
    if vol_ratio >= 4:
        msg = "*{0}\n量比：{1:.2f}\t跌幅：{2}%\n".format(code_name, vol_ratio, p_change)
        logging.debug(msg)
        return True
    else:
        return False


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
    strategy = '放量跌停'
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