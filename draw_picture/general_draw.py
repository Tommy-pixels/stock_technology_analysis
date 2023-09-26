from matplotlib import pyplot as plt
import numpy as np


class Draw:
    @classmethod
    def set_chinese(cls):
        """ plt设置显示中文"""
        plt.rcParams['font.sans-serif'] = ['SimHei']    # 正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号
        return

    @classmethod
    def draw_double_y(cls, title, x_series, y1_title, y1_series, y2_title, y2_series):
        """ 双y轴——共享x轴
        通常该类型x轴为时间
        """
        cls.set_chinese()
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title(title)
        ax1.set_ylabel(y1_title)
        _1 = ax1.plot(x_series, y1_series)
        # ax1.legend([y1_title], loc='best', fontsize='x-small')

        ax2 = ax1.twinx()
        ax2.set_ylabel(y2_title)
        _2 = ax2.plot(x_series, y2_series, 'r')

        ax2.set_xlabel('Date')
        # 图例
        plt.legend(handles=[_1[0], _2[0]], labels=[y1_title, y2_title], loc='upper left', fontsize='small')
        plt.show()
        return 1

    @classmethod
    def draw_linear_regression(cls, title, x_series, y_series):
        """线性回归图"""
        cls.set_chinese()
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title(title)
        _1 = ax1.plot(x_series, y_series, color='red')
        # plt.scatter()
        plt.show()
        return 1


if __name__ == '__main__':
    from single_stock.data_fetcher import Stock
    start_date = '20220901'
    period = 'daily'
    stock_instance = Stock()
    draw = Draw()
    single_stock_data = stock_instance.single_stock_data(stock_code='002855', period=period, start_date=start_date)
    # 动量图
    mom_result = stock_instance.caculate_indicator(
        stock_data=single_stock_data,
        indicators_lis=['收盘价动量']
    ).get('收盘价动量', None)
    draw.draw_double_y(
        title='收盘价动量',
        x_series=single_stock_data['日期'],
        y1_title='收盘价',
        y1_series=single_stock_data['收盘'],
        y2_title='动量',
        y2_series=mom_result
    )
    # # 线性回归
    # linear_result = stock_instance.caculate_indicator(
    #     stock_data=single_stock_data,
    #     indicators_lis=['线性回归角度']
    # ).get('线性回归角度', None)
    # draw.draw_linear_regression(
    #     title='线性回归角度',
    #     x_series=single_stock_data['日期'],
    #     y_series=single_stock_data['收盘'],
    # )
    import os
    os.system('pause')