# -*- encoding: UTF-8 -*-
import talib as tl
import pandas as pd
import logging
from draw_picture.general_draw import Draw

# 持续上涨（MA30向上）
def check(code_name, data, end_date=None, threshold=30):
    """30日简单移动均线指标 持续向上策略
    满足策略条件: ma30数据按等间隔分为三部分:每部分的首个数据的m30都要比前一个部分的首个数据的m30大，且最后一个日期的m30数据要大于首个数据的m30的1.2倍
    """
    # 1 检查数据表是否满足基本条件
    if(len(data) < threshold):
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return
    # 2 计算30日均线数据
    data['ma30'] = pd.Series(tl.MA(data['收盘'].values, 30), index=data.index.values)

    # 3 过滤数据-保留所需数据
    # 3.1 获取到指定日期为止的数据
    if(end_date is not None):
        mask = (data['日期'] <= end_date)
        data = data.loc[mask]

    # 3.2 获取最近 threshold 日的数据
    data = data.tail(n=threshold)

    # 4 策略判断——判断递增:
    #       数据按等间隔分为三部分:每部分的首个数据的m30都要比前一个部分的首个数据的m30大，且最后一个日期的m30数据要大于首个数据的m30的1.2倍
    check_result = False
    step1 = round(threshold/3)
    step2 = round(threshold*2/3)
    if(data.iloc[0]['ma30'] < data.iloc[step1]['ma30'] and data.iloc[step1]['ma30'] < data.iloc[step2]['ma30'] and data.iloc[step2]['ma30'] < data.iloc[-1]['ma30'] and data.iloc[-1]['ma30'] > 1.2 * data.iloc[0]['ma30']):
        check_result = True
    # 5 画图
    # Draw.draw_linear_regression(title=code_name, x_series=data['日期'], y_series=data['ma30'])
    return check_result