import talib
import pandas as pd


class General_Indicator:
    @classmethod
    def mom(cls, closing_price_series):
        """收盘价动量计算
        动量并不是价格走势的预测指标，而是反映了市场的整体情绪和基本面
        """
        return talib.MOM(closing_price_series)

    @classmethod
    def moving_average(cls, closing_price_series, timeperiod=10):
        """ 收盘价的简单移动均线指标 Simple Moving Average
        talib.MA() 同 talib.SMA()一样
        通常有 5日均线、10日均线、30日均线
        移动平均值中最重要的信息就是其斜率的方向。当斜率上升时，表示大众正在变得乐观——倾向于看多。它的斜率下降意味着大众开始变得悲观——倾向于看空。当价格升至移动平均值之上时，大众比之前乐观；当价格降至移动平均值之下时，大众比之前更悲观。
        """
        # close_price_array = pd.DataFrame(closing_price_series)
        # df_close = pd.DataFrame(closing_price_series, columns=['{}日移动平均'.format(str(timeperiod))])
        # ma_series = df_close.rolling(window=timeperiod).mean()
        ma_series = talib.MA(closing_price_series, timeperiod=timeperiod)     # 精准点
        return ma_series

    @classmethod
    def exponential_moving_average(cls, closing_price_series, timeperiod=12):
        """ 指数移动平均（EMA，Exponential Moving Average） ———— 一种更好的趋势跟随指标
        因为它为最近的价格分配了更大的权重而且对价格的反应也比简单的移动平均更灵敏。
        用法：
        -当要比较数值与均价的关系时，用 MA
        -要比较均价的趋势快慢时，用 EMA 更稳定。
        计算：EMA(t)=平滑常数*当前价格+(1-平滑常数)*EMA(t-1)
        表示t日的指数移动平均值，K表示平滑指数，一般取作2/(N+1)，N为几日的平均，EMA计算中的N一般选取12和26天，因此K相应为2/13和2/27。
        """
        # ema_series = closing_price_series.copy()  # 创造一个和cps一样大小的集合
        # for i in range(len(closing_price_series)):
        #     if(i == 0):
        #         ema_series[i] = closing_price_series[i]
        #     if(i > 0):
        #         ema_series[i] = ((timeperiod - 1) * ema_series[i - 1] + 2 * closing_price_series[i]) / (timeperiod + 1)
        ema_series = talib.EMA(closing_price_series, timeperiod=timeperiod)
        return ema_series

    @classmethod
    def moving_average_convergence_divergence(cls, closing_price_series):
        """ 指数平滑异同移动平均线（moving average convergence-divergence, MACD）：MACD线 和 MACD柱状线
        - MACD线
        MACD是以三个指数移动平均为基础，以两条曲线的形式出现在图表中，其两条线的交叉点，是一种交易信号。
        说明：
        由两条线组成：一条实线（叫作MACD线）和一条虚线（叫作信号线）。
        MACD线由两个指数移动平均（EMA）计算而来，其对价格的反应相对较快。MACD线和信号线的交点表明了市场中空方和多方实力变换的平衡点。
        信号线是以MACD线为基础，通过对MACD线以EMA的方式进行运算，实现对MACD线的平滑，其对价格变动的反应相对较慢。
        判断：在阿佩尔最初的体系中，较快的MACD线穿过较慢的信号线上升或者下降，为买入或者卖出的信号。
        MACD指标计算步骤：
        （1）计算12日收盘价的EMA；
        （2）计算26日收盘价的EMA；
        （3）用12日收盘价的EMA减去26日收盘价的EMA，将其差值画成一条实线，这就是较快的MACD线；也叫离差值（DIF）
        （4）计算这条实线的9日EMA，将其结果画成一条虚线，这就是较慢的信号线。也叫离差平均值（DEA）。
        （5）（DIF-DEA）×2即为MACD值。
        较快的MACD线反映的是短期内大众的心理变化，而较慢的信号线则反映了大众心理在较长期的变化。
        当较快的MACD线上升超过信号线时，表示多方主导了市场，这时候最好做多方；当较快的线落到较慢的信号线下面时，表示空方主导了市场，做空方比较有利。
        - MACD 柱状线
        相比原始的MACD线，MACD柱状线能够提供更深刻的关于多空力量均衡的信息。它不仅能分辨出哪种力量处于主导地位，而且能够分辨其力量是在逐渐增强还是在减弱。
        MACD柱状线=MACD线-信号线
        MACD柱状线测量的是MACD线和信号线之间的差值。它将差值画为一根根柱状线——为一系列垂直的线条。
        MACD柱状线的斜率方向揭示了市场中的主导力量。向上倾斜的MACD柱状线表示多方的力量在增强，而向下倾斜的MACD柱状线则意味着空方的力量在增强。
        """
        # ema_12_series = cls.exponential_moving_average(closing_price_series=closing_price_series, timeperiod=12)
        # ema_26_series = cls.exponential_moving_average(closing_price_series=closing_price_series, timeperiod=26)
        # dif_series = closing_price_series.copy()
        # for i in range(len(ema_12_series)):
        #     if(ema_12_series[i] == 'nan' or ema_26_series[i] == 'nan'):
        #         continue
        #     dif_series[i] = ema_12_series[i] - ema_26_series[i]
        # dea_series = cls.exponential_moving_average(closing_price_series=dif_series, timeperiod=9)
        # macd_series = closing_price_series.copy()
        # for i in range(len(closing_price_series)):
        #     dif = dif_series[i]
        #     dea = dea_series[i]
        #     if(dif == 'nan' or dea == 'nan'):
        #         macd = 'nan'
        #     else:
        #         macd = 2 * (dif - dea)
        #     macd_series[i] = macd
        # series_dic = {
        #     'dif_series': dif_series,
        #     'dea_series': dea_series,
        #     'macd_series': macd_series,
        # }
        series_dic = talib.MACD(
            closing_price_series,
            # fastperiod=12,
            # slowperiod=26,
            # signalperiod=9
        )
        return series_dic

    @classmethod
    def ease_of_movement_value(cls, highest_price_series, lowest_price_series, volume_series, fast_timeperiod=14, last_timeperiod=9):
        """ 简易波动指标（EMV，Ease of Movement Value）
        作用：将价格与成交量的变化结合成一个波动指标来反映股价或指数的变动状况 旨在先于其他投资者买入/卖出
        计算：
         A = （当日最高价 + 当日最低价）/ 2
         B = （前日最高价 + 前日最低价）/ 2
         C =  当日最高价 – 当日最低价
        (2)     当日EM = (A – B ) * C / 当日成交额
        (3)     EMV = EM的 N日的简单移动平均
        (4)     MAEMV = EMV的M日的简单移动平均
        (5)     参数N为14，参数M为9
        使用:
        - 当EMV值从下向上穿过零轴时，全仓买入；EMV值从上向下穿过零轴时，全仓卖出。
        - 如果较少的成交量便能推动股价上涨，则EMV数值会升高，相反的，股价下跌时也仅伴随较少的成交量，则EMV数值将降低。
        - 另一方面，倘若价格不涨不跌，或者价格的上涨和下跌，都伴随着较大的成交量时，则EMV的数值会趋近于零。
        - EMV指标曲线大部份集中在0轴下方，这个特征是EMV指标的主要特色，由于股价下跌一般成交量较少，EMV自然位于0轴下方，当成交量放大时，EMV又趋近于零，这可以说明EMV的理论精髓中，无法接受股价在涨升的过程，不断的出现高成交量消耗力气，反而认同徐缓成交的上涨，能够保存一定的元气，促使涨势能走得更远更长。从另外一个角度说，EMV重视移动长久且能产生足够利润的行情。
        - 关于EMV和EMV的平均线（MAEMV），两线的交叉并无意义，而是选择以EMV指标平均线跨越0轴为讯号，所产生的交易成果将更令人满意。
        :param highest_price_series 当日最高价
        :param lowest_price_series  当日最低价
        :param volume_series 成交量
        """
        series_dic = {
            'emv_series': None,
            'maemv_series': None,
        }
        em_series = highest_price_series.copy()
        for i in range(len(highest_price_series)):
            if(i-1<0):
                em = 'nan'
            else:
                A = 0.5 * (highest_price_series[i] + lowest_price_series[i])
                B = 0.5 * (highest_price_series[i-1] + lowest_price_series[i-1])
                C = highest_price_series[i] - lowest_price_series[i]
                em = (A - B) * C / volume_series[i]
            em_series[i] = em
        emv_series = talib.SMA(em_series, timeperiod=fast_timeperiod)
        maemv_series = talib.SMA(emv_series, timeperiod=last_timeperiod)
        series_dic['emv_series'] = emv_series
        series_dic['maemv_series'] = maemv_series
        return series_dic


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock
    stock_code = '002828'
    start_date = '20220901'
    period = 'daily'
    stock_instance = Stock()
    single_stock_data = stock_instance.single_stock_data(stock_code=stock_code, period=period, start_date=start_date)
    date_series = single_stock_data.get('日期').values  # 日期
    closing_price_series = single_stock_data.get('收盘').values  # 收盘价
    highest_price_series = single_stock_data.get('最高').values  # 最高价
    lowest_price_series = single_stock_data.get('最低').values  # 最低价
    volume_series = single_stock_data.get('成交量').values  # 成交量
    emv_series = General_Indicator.ease_of_movement_value(highest_price_series=highest_price_series, lowest_price_series=lowest_price_series, volume_series=volume_series)