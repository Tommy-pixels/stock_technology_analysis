import akshare as ak
import logging
import pandas as pd
import talib as tl
import concurrent.futures


class Base_Stock:
    @classmethod
    def all_stock_lis(cls):
        """获取所有股票列表"""
        all_data = ak.stock_zh_a_spot_em()
        subset = all_data[['代码', '名称']]
        stock_lis = [tuple(x) for x in subset.values]
        return stock_lis

    @classmethod
    def single_stock_data(cls, stock_code: str = '', period: str = "daily", start_date: str = "20220101", **kwargs):
        """ 获取单个个股数据
        :param stock_code: 股票代码
        :param start_date: 指定开始日期 20220101
        :param period: 什么区间的数据  'daily', 'weekly', 'monthly'
        :return:
        """
        stock = kwargs.get('stock', None)
        if(stock):
            stock_code = stock[0]
        else:
            pass
        if(not stock_code):
            print('股票码为空，获取股票数据失败')
            return None
        period_lis = ['daily', 'weekly', 'monthly']
        if(period not in period_lis):
            print('股票数据区间异常，获取股票 {} 数据失败，请确认股票数据区间为 {}'.format(
                stock_code, '/'.join(period_lis)
            ))
            return
        data = ak.stock_zh_a_hist(symbol=stock_code, period=period, start_date=start_date, adjust="qfq")
        if data is None or data.empty:
            logging.debug("股票：", stock_code + " 没有数据，略过...")
            return
        data['p_change'] = tl.ROC(data['收盘'], 1)
        pd.set_option('display.width', None)    # 取消省略号显示
        return data

    @classmethod
    def get_multi_stocks_data(cls, stock_code_lis:list, period: str = "daily", start_date: str = "20220101"):
        """获取多个个股票的数据
        :param stock_code_lis 股票码列表
        :param period: 什么区间的数据  'daily', 'weekly', 'monthly'
        """
        stocks_data_dic = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_to_stock = {
                executor.submit(
                    cls.single_stock_data, **{
                        'stock': stock,
                        'period': period,
                        'start_date': start_date
                    }
                ): stock for stock in stock_code_lis
            }
            for future in concurrent.futures.as_completed(future_to_stock):
                stock = future_to_stock[future]
                try:
                    data = future.result()
                    if data is not None:
                        data = data.astype({'成交量': 'double'})
                        stocks_data_dic[stock] = data
                except Exception as exc:
                    print('%s(%r) generated an exception: %s' % (stock[1], stock[0], exc))
        return stocks_data_dic