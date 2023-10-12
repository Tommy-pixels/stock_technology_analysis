# -*- encoding: UTF-8 -*-
"""选股操作
选用一些股票策略进行选股操作
"""
from single_stock.data_fetcher import Stock
# import settings
import strategy.enter as enter
from strategy import turtle_trade, climax_limitdown
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
from strategy import high_tight_flag
import akshare as ak
import logging
import time
from database.log import Tb_Log
from database.base import Tb_Stock_Info
from database.tb_matched_stock import Tb_Matched_Stock
from utils.common import Control_Time


class Stock_Choosen:
    @classmethod
    def statistics(cls, all_data, stocks):
        """统计数据"""
        limitup = len(all_data.loc[(all_data['涨跌幅'] >= 9.5)])
        limitdown = len(all_data.loc[(all_data['涨跌幅'] <= -9.5)])
        up5 = len(all_data.loc[(all_data['涨跌幅'] >= 5)])
        down5 = len(all_data.loc[(all_data['涨跌幅'] <= -5)])
        msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}".format(limitup, limitdown, up5, down5)
        print(msg)
        return limitup, limitdown, up5, down5

    @classmethod
    def check_enter(cls, end_date=None, strategy_fun=enter.check_volume):
        def end_date_filter(stock_data):
            if(end_date is not None):
                if(end_date < stock_data[1].iloc[0]['日期']):  # 该股票在end_date时还未上市
                    logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                    return False
            return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)
        return end_date_filter

    @classmethod
    def check(cls, stocks_data, strategy, strategy_func, end_date):
        checked_stock_lis = []
        m_filter = cls.check_enter(end_date=end_date, strategy_fun=strategy_func)    # 过滤函数
        results = dict(filter(m_filter, stocks_data.items()))
        if(len(results) > 0):
            print('**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(strategy, list(results.keys())))
            # push.strategy('**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(strategy, list(results.keys())))
            checked_stock_lis = list(results.keys())
        return checked_stock_lis

    @classmethod
    def process(cls, stocks, strategies, start_date, end_date, **kwargs):
        operation_id = kwargs.get('operation_id', '')
        action_name = '策略选股'
        cursor = Tb_Log.get_cursor()
        for _ in stocks:
            stock_code = _[0]
            stock_name = _[1]
            # 1 获取股票数据
            for i in range(3):
                try:
                    stocks_data = Stock.get_multi_stocks_data(
                        stock_code_lis=[_],
                        period="daily",
                        start_date=start_date.replace('-', '')
                    )
                except Exception as e:
                    print('请求股票数据接口异常，等待15s重新请求')
                    time.sleep(15)
                    stocks_data = Stock.get_multi_stocks_data(
                        stock_code_lis=[_],
                        period="daily",
                        start_date=start_date.replace('-', '')
                    )
                if (stocks_data is not None and stocks_data[_] is not None and not stocks_data[_].empty):
                    break
            if (stocks_data[_] is None):
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
            # 2 股票数据范围过滤
            if(end_date):
                mask = (stocks_data[_]['日期'] <= end_date)
                stocks_data[_] = stocks_data[_].loc[mask]
            # 逐个策略执行
            for strategy, strategy_func in strategies.items():
                checked_stock_lis = cls.check(stocks_data, strategy, strategy_func, end_date)
                # 记录满足条件的股票
                if(checked_stock_lis):
                    base_data_start_date = stocks_data[_].iloc[0]['日期']
                    base_data_end_date = stocks_data[_].iloc[len(stocks_data[_]) - 1]['日期']
                    Tb_Log.create_log(
                        cursor=cursor,
                        operation_id=operation_id,
                        action=action_name,
                        action_detail=strategy,
                        action_status='满足策略',
                        create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
                        stock_lis=checked_stock_lis,
                        trace_start_date=base_data_start_date,
                        trace_end_date=base_data_end_date
                    )
                    # 添加到选股表
                    for _stock in checked_stock_lis:
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
                            stock=_stock,
                            note=''
                        )
                time.sleep(2)
        return 1

    @classmethod
    def run(cls, start_date, end_date):
        """执行选股操作"""
        logging.info("************************ process start ***************************************")
        action_name = '策略运行'
        operation_id = Tb_Log.generate_operation_id(name=action_name)

        # 1 获取股票列表
        all_data = ak.stock_zh_a_spot_em()
        subset = all_data[['代码', '名称']]
        stocks = [tuple(x) for x in subset.values]
        stock_info_inst = Tb_Stock_Info()
        cursor = stock_info_inst.get_cursor()
        stocks = stock_info_inst.filter_stock_info(
            cursor=cursor,
            belong_lis=['深市A股', '沪市A股']
        )   # 从数据库获取需要运行策略的股票信息列表
        Tb_Log.create_log(
            cursor=cursor,
            operation_id=operation_id,
            action='多策略回测',
            action_detail='',
            action_status='启动多策略回测',
            create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
            stock_lis=stocks
        )

        # 2 股票统计数据
        limitup, limitdown, up5, down5 = cls.statistics(all_data, stocks)
        Tb_Log.create_log(
            cursor=cursor,
            operation_id=operation_id,
            action='股票情况统计',
            action_detail='涨停数;跌停数;涨幅大于5%数;跌幅大于5%数',
            action_status='股票情况统计完成',
            create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
            statistics_dic={
                'limitup': limitup,
                'limitdown': limitdown,
                'up5': up5,
                'down5': down5,
            }
        )

        # 3 策略执行
        # 选用策略
        strategies_dic = {
            '放量上涨': enter.check_volume,
            '均线多头': keep_increasing.check,
            '停机坪': parking_apron.check,
            '回踩年线': backtrace_ma250.check,
            '突破平台': breakthrough_platform.check,
            '无大幅回撤': low_backtrace_increase.check,
            '海龟交易法则': turtle_trade.check_enter,
            '高而窄的旗形': high_tight_flag.check,
            '放量跌停': climax_limitdown.check,
        }

        # 执行选股操作
        cls.process(stocks=stocks, strategies=strategies_dic, start_date=start_date, end_date=end_date, operation_id=operation_id)
        logging.info("************************ process   end ***************************************")
        return 1


if __name__ == '__main__':
    start_date = '2022-09-01'
    end_date = '2023-10-10'
    Stock_Choosen.run(start_date=start_date, end_date=end_date)
