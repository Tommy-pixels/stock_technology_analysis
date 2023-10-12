# -*- encoding: UTF-8 -*-
import logging
# import setting


# 高而窄的旗形
def check(code_name, data, end_date=None, threshold=60):
    # 龙虎榜上必须有机构
    # if(code_name[0] not in settings.top_list):
    #     return False

    if end_date is not None:
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]
    data = data.tail(n=threshold)

    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    data = data.tail(n=14)
    low = data['最低'].min()
    ratio_increase = data.iloc[-1]['最高'] / low
    if ratio_increase < 1.9:
        return False

    previous_p_change = 0.0
    # 连续两天涨幅大于等于10%
    for _p_change in data['p_change'].values:
        if _p_change >= 9.5:
            if previous_p_change >= 9.5:
                return True
            else:
                previous_p_change = _p_change
        else:
            previous_p_change = 0.0
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
    strategy = '高而窄的旗形'
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
