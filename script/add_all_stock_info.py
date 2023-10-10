"""将所有股票录入数据库"""
from single_stock.data_fetcher import Stock
from database.base import Tb_Stock_Info
from database.log import Tb_Log
from utils.common import Control_Time

def run():
    success_lis = []
    fail_lis = []
    stock_instance = Stock()
    all_stock_lis = stock_instance.all_stock_lis()
    stock_info_inst = Tb_Stock_Info()
    cursor = stock_info_inst.get_cursor()
    action_name = '录入股票基本信息'
    operation_id = Tb_Log.generate_operation_id(name=action_name)
    for stock in all_stock_lis:
        stock_code = stock[0]
        stock_name = stock[1]
        '''
        新三板转上来到北交所的股票基础层43、创新层83、精选层87、新上北交所88。
        '''
        note = ''
        if(stock_code.startswith('6')):
            if (stock_code.startswith('600') or stock_code.startswith('601') or stock_code.startswith('603') or stock_code.startswith('605')):
                belong = '沪市A股'
            elif(stock_code.startswith('688')):
                belong = '科创板'
            elif(stock_code.startswith('689')):
                belong = '科创板'
                note = 'CDR存托凭'
        elif (stock_code.startswith('900')):
            belong = '沪市B股'
        elif(stock_code.startswith('00') or stock_code.startswith('30')):
            if (stock_code.startswith('300') or stock_code.startswith('301')):
                belong = '创业板'
            elif (stock_code.startswith('000') or stock_code.startswith('001') or stock_code.startswith('002') or stock_code.startswith('003')):
                belong = '深市A股'
                if(stock_code.startswith('002')):
                    note = '中小板'  # 深市
        elif (stock_code.startswith('200')):
            belong = '深市B股'
        elif(stock_code.startswith('700')):
            belong = '沪市配股'
        elif (stock_code.startswith('080')):
            belong = '深市配股'
        elif (stock_code.startswith('580')):
            belong = '沪市权证'
        elif (stock_code.startswith('031')):
            belong = '深市权证'
        elif(stock_code.startswith('8')):
            if(stock_code.startswith('82')):
                belong = '北交所优先股'
            elif(stock_code.startswith('83') or stock_code.startswith('87')):
                belong = '北交所普通股'
            elif(stock_code.startswith('88')):
                belong = '北交所公开发行'
            else:
                belong = '北交所'
        elif(stock_code.startswith('43')):
            belong = '新三板'
        else:
            belong = ''
            note = ''
        insert_res = stock_info_inst.add_stock_info(
            cursor=cursor,
            stock_name=stock_name,
            stock_code=stock_code,
            belong=belong,
            note=note
        )
        if(insert_res):
            success_lis.append(stock)
        else:
            fail_lis.append(stock)
    if(len(success_lis) == len(all_stock_lis)):
        print('所有股票录入完成，共{}只股'.format(str(len(success_lis))))
        action_status = '全部录入完成'
    else:
        print('成功录入股票 {} 只，共有 {} 只'.format(str(len(success_lis)), str(len(all_stock_lis))))
        action_status = '部分录入完成'
    Tb_Log.create_log(
        cursor=cursor,
        operation_id=operation_id,
        action='录入股票基本信息',
        action_status=action_status,
        create_time=Control_Time.get_cur_date('%Y-%m-%d %H:%M:%S'),
        fail_lis=fail_lis,
        excuting_file='add_all_stock_info.py',
        note=''
    )
    return 1


if __name__ == '__main__':
    print('录入股票基本信息')
    run()