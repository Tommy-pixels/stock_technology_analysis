import talib


class General_Indicator:
    @classmethod
    def mom(cls, closing_price_series):
        """收盘价动量计算
        动量并不是价格走势的预测指标，而是反映了市场的整体情绪和基本面
        """
        return talib.MOM(closing_price_series)