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
# from strategy import high_tight_flag
import akshare as ak
import logging
import time
import datetime


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
        return 1

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
        # end = settings.config['end_date']
        m_filter = cls.check_enter(end_date=end_date, strategy_fun=strategy_func)    # 过滤函数
        results = dict(filter(m_filter, stocks_data.items()))
        if len(results) > 0:
            print('**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(strategy, list(results.keys())))
            # push.strategy('**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(strategy, list(results.keys())))

    @classmethod
    def process(cls, stocks, strategies, end_date):
        for _ in stocks:
            stock_code = _[0]
            stock_name = _[1]
            if (stock_code.startswith('3') or stock_code.startswith('688') or stock_code.startswith('8')):
                continue
            stocks_data = Stock.get_multi_stocks_data(
                stock_code_lis=[_]
            )
            # 逐个策略执行
            for strategy, strategy_func in strategies.items():
                cls.check(stocks_data, strategy, strategy_func, end_date)
                time.sleep(2)

    @classmethod
    def run(cls, end_date):
        """执行选股操作"""
        logging.info("************************ process start ***************************************")
        all_data = ak.stock_zh_a_spot_em()
        subset = all_data[['代码', '名称']]
        stocks = [tuple(x) for x in subset.values]
        cls.statistics(all_data, stocks)

        # 选用策略
        strategies_dic = {
            '放量上涨': enter.check_volume,
            '均线多头': keep_increasing.check,
            '停机坪': parking_apron.check,
            '回踩年线': backtrace_ma250.check,
            # '突破平台': breakthrough_platform.check,
            '无大幅回撤': low_backtrace_increase.check,
            '海龟交易法则': turtle_trade.check_enter,
            # '高而窄的旗形': high_tight_flag.check,
            '放量跌停': climax_limitdown.check,
        }

        if datetime.datetime.now().weekday() == 0:
            strategies_dic['均线多头'] = keep_increasing.check
        # 执行选股操作
        cls.process(stocks, strategies_dic, end_date)
        logging.info("************************ process   end ***************************************")
        return 1


if __name__ == '__main__':
    end_date = '20231008'
    Stock_Choosen.run(end_date=end_date)
