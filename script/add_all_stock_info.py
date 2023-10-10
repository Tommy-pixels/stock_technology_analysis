"""将所有股票录入数据库"""
from single_stock.data_fetcher import Stock
from database.base import Tb_Stock_Info


def run():
    success_lis = []
    stock_instance = Stock()
    all_stock_lis = stock_instance.all_stock_lis()
    stock_info_inst = Tb_Stock_Info()
    cursor = stock_info_inst.get_cursor()
    for stock in all_stock_lis:
        stock_code = stock[0]
        stock_name = stock[1]
        if(stock_code.startswith('688')):
            belong = '科创板'
        elif(stock_code.startswith('002')):
            belong = '中小板'
        elif (stock_code.startswith('300')):
            belong = '创业板'
        elif (stock_code.startswith('600') or stock_code.startswith('601') or stock_code.startswith('603') or stock_code.startswith('605')):
            belong = '沪市A股'
        elif (stock_code.startswith('900')):
            belong = '沪市B股'
        elif (stock_code.startswith('000')):
            belong = '深市A股'
        elif (stock_code.startswith('200')):
            belong = '深市B股'
        elif(stock_code.startswith('700')):
            belong = '沪市配股'
        elif(stock_code.startswith('080')):
            belong = '深市配股'
        elif (stock_code.startswith('580')):
            belong = '沪市权证'
        elif (stock_code.startswith('031')):
            belong = '深市权证'
        insert_res = stock_info_inst.add_stock_info(
            cursor=cursor,
            stock_name=stock_name,
            stock_code=stock_code,
            belong=belong,
            note=''
        )
        if(insert_res):
            success_lis.append(stock)
    if(len(success_lis) == len(all_stock_lis)):
        print('所有股票录入完成，共{}只股'.format(str(len(success_lis))))
    else:
        print('成功录入股票 {} 只，共有 {} 只'.format(str(len(success_lis)), str(len(all_stock_lis))))
    return 1


if __name__ == '__main__':
    print('录入股票数据')
    run()