import json
from .base import Base_DB


class Tb_Matched_Stock(Base_DB):
    """ 选股表——策略选中的股票表
    `id` int NOT NULL AUTO_INCREMENT,
    `matched_strategy` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '符合策略选择',
    `base_data_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '基数据类型 daily/monthly',
    `base_data_start_date` datetime NULL DEFAULT NULL COMMENT '基数据开始日期',
    `base_data_end_date`datetime NULL DEFAULT NULL COMMENT '基数据结束日期',
    `base_data_detail` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '基数据详细 包括 数据起止日期等',
    `stock_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `stock_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `extra_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    `backtrace_time` datetime NULL DEFAULT NULL,
    `note` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    """
    def __init__(self):
        __TB_NAME__ = 'tb_matched_stock'

    @classmethod
    def add_matched_stock(cls, cursor, operation_id, matched_strategy:str, matched_stock:tuple, base_data_type:str, base_data_start_date:str, base_data_end_date:str, base_data_detail:dict, backtrace_time:str, **kwargs):
        """ 添加策略选中的股票到股票选中库
        :param base_data_type 基数据类型 daily/monthly
        :param base_data_detail 基数据详细   包括用于回测的起止日期
        """
        result = False
        stock_code = matched_stock[0]
        stock_name = matched_stock[1]
        note = kwargs.get('note', '')
        try:
            kwargs.pop('note')
        except Exception as e:
            pass
        if(base_data_detail):
            base_data_detail = json.dumps(base_data_detail, ensure_ascii=False)
        else:
            base_data_detail = ''
        extra_info = json.dumps(kwargs, ensure_ascii=False)
        sql = "INSERT INTO tb_matched_stock (" \
              "operation_id, matched_strategy, base_data_type, base_data_start_date, base_data_end_date, base_data_detail, stock_name, stock_code, extra_info, backtrace_time, note) VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');".format(
            operation_id, matched_strategy, base_data_type, base_data_start_date, base_data_end_date, base_data_detail, stock_name, stock_code, extra_info, backtrace_time, note
        )
        try:
            cursor.execute(sql)
            result = True
        except Exception as e:
            print('sql执行异常：', sql)
        return result

