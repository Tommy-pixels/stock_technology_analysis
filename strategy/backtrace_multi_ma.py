# -*- encoding: UTF-8 -*-
import time
import talib as tl
import pandas as pd
import logging
from datetime import datetime, timedelta


def check_increasing(data, threshold=30):
    """判断多头"""
    # 1 获取最近 threshold 日的数据
    data = data.tail(n=threshold)
    # 2 策略判断——判断递增:
    #       数据按等间隔分为三部分:每部分的首个数据的m30都要比前一个部分的首个数据的m30大，且最后一个日期的m30数据要大于首个数据的m30的1.2倍
    check_result = False
    step1 = round(threshold / 3)
    step2 = round(threshold * 2 / 3)
    if (data.iloc[0] < data.iloc[step1] and data.iloc[step1] < data.iloc[step2] and
        data.iloc[step2] < data.iloc[-1] and data.iloc[-1] > 1.2 * data.iloc[0]):
        check_result = True
    return check_result

def check(code_name, data, end_date=None, threshold=60):
    """ 多头排列
    多头排列首先是一个均线排列形态，能够预判趋势目前是多头占上风的。而这个预判背后所支撑的逻辑，源于均线的排列方式。
    人们在长期使用均线这个指标的过程中，通过总结经验和数据，认为均线的排列可以粗分为两种情况：多头排列和空头排列。
    多头排列就是市场趋势是强势上升势，均线在5—10—20—40—120K线下支撑排列向上为多头排列。我们先看一个简单的三均线多头排列形态。
    多头排列形态的判定标准是：
        短期均线依次在长期均线之上，因此股价有较好的支撑。说的再简单一些，如果把均线理解为买入成本的平均值，均线排列依次短期线、中期线、长期线由上而下依次排列，这说明我们过去买进的成本很低，做短线的、中线的、长线的都有赚头，市场一片向上均线多头排列趋势为强势上升势，操作思维为多头思维。
    回踩点:就是价格前期冲高后出现了小幅回调下行
    在这个策略中，回踩是有条件的，即回踩幅度并没有破坏均线多头排列的格局。在这种情况下，由于每一条不同周期的均线都是支撑，所以回撤往往成为一个较理想的进场点位。
    假如某只股票，前期多头排列，但是回踩之后，整体均线形态受到巨大破坏，那么这只股票就不符合我们的筛选条件了。
    回踩点能够具体的量化，如果在多头排列的状态下当根K线击穿了10日均线，那么可以视作这根K线是一个回踩点，发出买入信号。
    """
    # 1 检查数据表是否满足基本条件
    if (data is None or len(data) < 250):
        logging.debug("{0}:样本小于250天...\n".format(code_name))
        return
    begin_date = data.iloc[0]['日期']
    if (end_date is not None):
        if (end_date < begin_date):  # 该股票在end_date时还未上市
            logging.debug("{}在{}时还未上市".format(code_name, end_date))
            return False
    # 2 均线计算    短期均线值依次大于长期均线值
    ma_list = [5, 10, 20, 60, 120]
    for ma in ma_list:
        data['ma' + str(ma)] = pd.Series(tl.MA(data['收盘'].values, ma), index=data.index.values)
        check_duotou = check_increasing(data=data['ma' + str(ma)])
        if(not check_duotou):
            print("{0}:{1}非多头排列...\n".format(code_name, 'ma' + str(ma)))
            logging.debug("{0}:{1}非多头排列...\n".format(code_name, 'ma' + str(ma)))
            return False
    # 3 过滤数据-保留所需数据
    # 3.1 获取到指定日期为止的数据
    if (end_date is not None):
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    # 3.2 获取最近 threshold 日的数据
    data = data.tail(n=threshold)

    # 回踩点的定义为当根K线击穿10日均线，未击穿更长周期均线，并仍满足多头排列
    # 买入股票数上限为100只，等权重买入，当持有股票数100只时，有股票卖出才买入股票
    # 买入时机：多头策略回踩点的第二天开盘买入
    # 卖出时机：当5日均线下穿40日均线，第二天开盘卖出
    # 函数：求满足开仓条件的股票列表
    mask = ((data['ma5'] > data['ma10']) & (data['ma10'] > data['ma20']) & (data['ma20'] > data['ma60']) & (data['ma60'] > data['ma120']))
    # mask = ((data['ma5'] > data['ma10']))
    data = data.loc[mask]
    # if(data.iloc[-1]['日期'] == '2023-10-09' and abs(data.iloc[-1]['最低'] - data.iloc[-1]['ma10'])<=0.15):
    if (abs(data.iloc[-1]['最低'] - data.iloc[-1]['ma10']) <= 1.5):
        return True
    return False

if __name__ == '__main__':
    """
    ('605068', '明新旭腾')
    ('603667', '五洲新春')
    """
    from single_stock.data_fetcher import Stock
    from database.base import Tb_Stock_Info
    from database.log import Tb_Log
    from database.tb_matched_stock import Tb_Matched_Stock
    from utils.common import Control_Time

    stock_instance = Stock()
    # stocks = stock_instance.all_stock_lis()
    stock_info_inst = Tb_Stock_Info()
    cursor = stock_info_inst.get_cursor()
    stocks = stock_info_inst.filter_stock_info(
        cursor=cursor, belong_lis=['沪市A股', '深市A股']
    )
    cursor.close()
    start_date = '2022-05-01'
    end_date = '2023-10-10'
    strategy = '多头排列递增'
    action_name = '策略选股-' + strategy
    operation_id = Tb_Log.generate_operation_id(name=action_name)
    cursor = Tb_Log.get_cursor()
    for _ in stocks:
        stock_code = _[0]
        stock_name = _[1]
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
        if(check(code_name=_, data=data, end_date=end_date, threshold=60)):
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