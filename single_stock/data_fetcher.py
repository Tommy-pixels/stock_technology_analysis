# -*- encoding: UTF-8 -*-
"""获取股票数据"""
from single_stock.base import Base_Stock
from indicators.general_indicator import General_Indicator
import talib
from talib import MA_Type


class Stock(Base_Stock):
    @staticmethod
    def print_reuslt(key_base, series_base, key_lis, series_lis):
        """格式化打印"""
        key_s = key_base
        for key in key_lis:
            key_s = key_s + '  ' + key
        print(key_s)
        for i in range(len(series_base)):
            _ = str(series_base[i])
            for i2 in range(len(series_lis)):
                _ = _ + '  ' + str(series_lis[i2][i])
            print(_)
        return 1

    @classmethod
    def caculate_indicator(cls, stock_data, indicators_lis, **kwargs):
        """指标运算
        :param indicators_lis 需要计算的指标
        """
        result_dic = {}
        stock_code = kwargs.get('stock_code', '')
        period = kwargs.get('period', '')
        start_date = kwargs.get('start_date', '')
        if(not indicators_lis):
            print('待计算指标列表为空，退出')
            return
        check_exist_stock_data = len(stock_data.get('开盘', '')) <= 1
        if(check_exist_stock_data and (not stock_code or not period or not start_date)):
            print('股票数据为空 且 股票代码/时间区间/开始日期为空，计算失败')
            return
        if(check_exist_stock_data):
            stock_data = cls.single_stock_data(
                stock_code=stock_code,
                period=period,
                start_date=start_date
            )
            if(not stock_data):
                print('获取到股票 {} {} 数据为空，计算失败'.format(stock_code, period))
                return
        # 1 提取个股各类数据
        date_series = stock_data.get('日期').values   # 日期
        opening_price_series = stock_data.get('开盘').values
        closing_price_series = stock_data.get('收盘').values     # 收盘价数据
        high_series = stock_data.get('最高').values   # 最高价
        low_series = stock_data.get('最低').values   # 最低价
        volume_series = stock_data.get('成交量').values  # 成交量

        # 2 各类指标计算
        for indicator in indicators_lis:
            if(indicator == '简单移动平均数SMA'):
                ## 简单移动平均数SMA
                sma_result = talib.SMA(closing_price_series)
                print('简单移动平均数SMA：')
                cls.print_reuslt(
                    key_base='收盘价',
                    series_base=closing_price_series,
                    key_lis=['简单移动平均数SMA'],
                    series_lis=[sma_result]
                )
            elif(indicator == '收盘价动量'):
                ## 收盘价动量计算
                mom_result = talib.MOM(closing_price_series, timeperiod=5)
                result_dic['收盘价动量'] = mom_result
                print('收盘价的动量指标:')
                cls.print_reuslt(
                    key_base='收盘价',
                    series_base=closing_price_series,
                    key_lis=['收盘价动量'],
                    series_lis=[mom_result]
                )
            elif(indicator == '三指数移动平均'):
                ## 布林线 三指数移动平均
                upper, middle, lower = talib.BBANDS(closing_price_series, matype=MA_Type.T3)
                print('三指数移动平均: ')
                cls.print_reuslt(
                    key_base='收盘价',
                    series_base=closing_price_series,
                    key_lis=[' 上 ', ' 中 ', ' 下 '],
                    series_lis=[upper, middle, lower]
                )
            elif(indicator == 'RSI'):
                # RSI通常时间段是14天内
                timeperiod = 14     # 时间区间
                rsi_result = talib.RSI(closing_price_series, timeperiod=timeperiod)
                result_dic['RSI'] = rsi_result
                cls.print_reuslt(
                    key_base='收盘价',
                    series_base=closing_price_series,
                    key_lis=[' RSI '],
                    series_lis=[rsi_result]
                )
            elif(indicator == 'ADX'):
                timeperiod = 14
                high = high_series
                low = low_series
                adx_result = talib.ADX(
                    high=high,  # 最高价
                    low=low,    # 最低价
                    close=closing_price_series,     # 收盘价
                    timeperiod=timeperiod   # 时间区间
                )
                result_dic['ADX'] = adx_result
                cls.print_reuslt(
                    key_base='收盘价',
                    series_base=closing_price_series,
                    key_lis=[' ADX '],
                    series_lis=[adx_result]
                )
            elif(indicator == '线性回归角度'):
                timeperiod = 14
                linearreg_result = talib.LINEARREG_ANGLE(
                    real=closing_price_series,  # 收盘价
                    timeperiod=timeperiod  # 时间区间
                )
                result_dic['线性回归角度'] = linearreg_result
                cls.print_reuslt(
                    key_base='收盘价',
                    series_base=closing_price_series,
                    key_lis=[' 线性回归 '],
                    series_lis=[linearreg_result]
                )
            elif(indicator == '简易波动指标'):
                fast_timeperiod=14
                last_timeperiod=9
                series_dic = General_Indicator.ease_of_movement_value(
                    highest_price_series=high_series,
                    lowest_price_series=low_series,
                    volume_series=volume_series
                )
                result_dic['简易波动指标'] = series_dic
        return result_dic


if __name__ == '__main__':
    # data = fetch(['002434'])
    # 002828 贝肯能源
    stock_code_lis = ['600355']
    start_date = '20221009'
    period = 'daily'
    stock_instance = Stock()
    single_stock_data = stock_instance.single_stock_data(stock_code='002828', period=period, start_date=start_date)
    # stocks_data = stock_instance.get_multi_stocks_data(stock_code_lis=stock_code_lis, period=period, start_date=start_date)
    indicators_lis = [
        # '简单移动平均数SMA',
        # '收盘价动量',
        # '三指数移动平均',
        'RSI',
        # 'ADX',
        # '线性回归角度'
    ]
    stock_instance.caculate_indicator(stock_data=single_stock_data, indicators_lis=indicators_lis)
    print()