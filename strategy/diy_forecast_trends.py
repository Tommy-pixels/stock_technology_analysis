"""
指标运用选股
- RSI预测看涨，并在ADX突破25时确认趋势 看adx是否成线性回归递增
"""


class Forecase_Trend:
    """趋势预测"""
    @classmethod
    def forecast(cls, stock_data, **kwargs):
        """
        预测条件:
            - RSI预测看涨(RSI<30为超卖、RSI>70为超买)，并在ADX突破25时确认趋势
        :param stock_data:
        :param kwargs:
        :return:
        """
        date_series = stock_data.get('日期').values  # 日期
        closing_price_series = stock_data.get('收盘').values  # 收盘价
        # 1 计算指标
        rsi_series = Stock.caculate_indicator(stock_data=stock_data, indicators_lis=['RSI'], **kwargs).get('RSI', [])
        adx_series = Stock.caculate_indicator(stock_data=stock_data, indicators_lis=['ADX'], **kwargs).get('ADX', [])

        # 2 条件判断
        zuhe_lis = zip(list(date_series), closing_price_series, list(rsi_series), list(adx_series))
        print('date    price    rsi    adx')
        for _ in zuhe_lis:
            date = _[0]
            closing_price = str(_[1])
            rsi = str(_[2])
            adx = str(_[3])
            content = '{}  {}  {}  {}\t\t'.format(date, closing_price, rsi, adx)
            if(not rsi or not adx or rsi=='nan' or adx == 'nan'):
                continue
            if(float(rsi)<30):
                content = content + '超卖'
            elif(float(rsi) > 70):
                content = content + '超买'
            else:
                content = content + '正常'

            if(float(adx) < 25):
                content = content + '-' + '趋势未成'
            elif(float(adx) > 25 and float(adx) < 45):
                content = content + '-' + '趋势已成,正常强度'
            elif(float(adx) >= 45 and float(adx) < 65):
                content = content + '-' + '趋势已成,稍强'
            else:
                content = content + '-' + '趋势已成,很强'
            print(content)
        return 1


    @classmethod
    def run(cls, stock_code, **kwargs):
        return 1


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock

    forecast_trend = Forecase_Trend()
    stock_code = '002855'
    start_date = '20220901'
    period = 'daily'
    stock_instance = Stock()
    single_stock_data = stock_instance.single_stock_data(stock_code=stock_code, period=period, start_date=start_date)
    forecast_trend.forecast(stock_data=single_stock_data)
    print()