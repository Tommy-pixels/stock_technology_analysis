"""
更新添加所有股票的日数据
"""
import time
from single_stock.data_fetcher import Stock
from database.base import Tb_Stock_Info, Tb_Stock_Daily_Data
from database.log import Tb_Log
from utils.common import Control_Time


def run():
    # 1 创建实例
    stock_info_inst = Tb_Stock_Info()
    stock_daily_data_inst = Tb_Stock_Daily_Data()
    stock_inst = Stock()
    cursor = stock_info_inst.get_cursor()
    action_name = '录入股票日数据'
    operation_id = Tb_Log.generate_operation_id(name=action_name)

    # 2 获取要提取日数据的股票列表
    stock_lis = stock_info_inst.filter_stock_info(cursor=cursor, belong_lis=['沪市A股', '深市A股'])
    # 3 获取股票日数据并录入数据库
    for stock in stock_lis:
        stock_code = stock[0]
        if(stock_code.startswith('00')):
            # 深市 股市成立时间19910703
            data = stock_inst.single_stock_data(
                stock=stock,
                period='daily',
                start_date='19910703'
            )
        else:
            # 沪市 股市成立时间19901219
            data = stock_inst.single_stock_data(
                stock=stock,
                period='daily',
                start_date='19901219'
            )
        if(data is None or data.empty):
            # 添加操作记录
            action_status = '获取到日数据为空'
            Tb_Log.create_log(
                cursor=cursor,
                operation_id=operation_id,
                action='录入股票日数据',
                action_detail=stock[0] + '-' + stock[1],
                action_status=action_status,
                create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
                stock=stock,
                excuting_file='add_all_stock_daily_data.py',
                note=''
            )
            continue
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
            action_status = '录入数据完成，共{}条'.format(total)
        else:
            print('Error: {} 日数据共 {} 条，录入 {} 条'.format(stock, total, len(success_lis)))
            action_status = '录入数据不全'
        # 添加操作记录
        Tb_Log.create_log(
            cursor=cursor,
            operation_id=operation_id,
            action='录入股票日数据',
            action_detail=stock[0] + '-' + stock[1],
            action_status=action_status,
            create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
            stock=stock,
            start_end_date_section=[data.iloc[0]['日期'], data.iloc[len(data)-1]['日期']],    # 起止日期
            excuting_file='add_all_stock_daily_data.py',
            note=''
        )
        time.sleep(5)


if __name__ == '__main__':
    print('录入股票日数据')
    run()