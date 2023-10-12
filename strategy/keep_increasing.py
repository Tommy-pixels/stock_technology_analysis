# -*- encoding: UTF-8 -*-
import talib as tl
import pandas as pd
import logging
from draw_picture.general_draw import Draw
import time


# 持续上涨（MA30向上）
def check(code_name, data, end_date=None, threshold=30):
    """30日简单移动均线指标 持续向上策略
    满足策略条件: ma30数据按等间隔分为三部分:每部分的首个数据的m30都要比前一个部分的首个数据的m30大，且最后一个日期的m30数据要大于首个数据的m30的1.2倍
    """
    # 1 检查数据表是否满足基本条件
    if(len(data) < threshold):
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return
    # 2 计算30日均线数据
    data['ma30'] = pd.Series(tl.MA(data['收盘'].values, 30), index=data.index.values)

    # 3 过滤数据-保留所需数据
    # 3.1 获取到指定日期为止的数据
    if(end_date is not None):
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    # 3.2 获取最近 threshold 日的数据
    data = data.tail(n=threshold)

    # 4 策略判断——判断递增:
    #       数据按等间隔分为三部分:每部分的首个数据的m30都要比前一个部分的首个数据的m30大，且最后一个日期的m30数据要大于首个数据的m30的1.2倍
    check_result = False
    step1 = round(threshold/3)
    step2 = round(threshold*2/3)
    if(data.iloc[0]['ma30'] < data.iloc[step1]['ma30'] and data.iloc[step1]['ma30'] < data.iloc[step2]['ma30'] and data.iloc[step2]['ma30'] < data.iloc[-1]['ma30'] and data.iloc[-1]['ma30'] > 1.2 * data.iloc[0]['ma30']):
        check_result = True
    # 5 画图
    # Draw.draw_linear_regression(title=code_name, x_series=data['日期'], y_series=data['ma30'])
    return check_result


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock
    stock_instance = Stock()
    stocks = stock_instance.all_stock_lis()
    from database.log import Tb_Log
    from database.base import Tb_Stock_Info
    from database.tb_matched_stock import Tb_Matched_Stock
    from utils.common import Control_Time
    cursor = Tb_Stock_Info.get_cursor()
    stocks = Tb_Stock_Info.filter_stock_info(
        cursor=cursor,
        belong_lis=['沪市A股', '深市A股']
    )
    cursor.close()
    del cursor
    start_date = '2022-05-01'
    end_date = '2023-10-10'
    strategy = '30均线指标递增指标策略'
    action_name = '策略选股-' + strategy
    operation_id = Tb_Log.generate_operation_id(name=action_name)
    cursor = Tb_Log.get_cursor()
    for _ in stocks:
        stock_code = _[0]
        stock_name = _[1]
        if (stock_code.startswith('3') or stock_code.startswith('688') or stock_code.startswith('8')):
            continue
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
        if(end_date):
            mask = (data['日期'] <= end_date)
            data = data.loc[mask]
        if (check(code_name=_, data=data, end_date=end_date, threshold=30)):
            print('满足{}策略：{}'.format(strategy, _))
            base_data_start_date = data.iloc[0]['日期']
            base_data_end_date = data.iloc[len(data) - 1]['日期']
            action_status = '满足策略'
            Tb_Log.create_log(
                cursor=cursor,
                operation_id=operation_id,
                action=action_name,
                action_detail=_[0] + '-' + _[1],
                action_status=action_status,
                create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
                stock=_,
                trace_start_date=base_data_start_date,
                trace_end_date=base_data_end_date
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