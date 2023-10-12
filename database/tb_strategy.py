"""
策略相关
"""
import json
from .base import Base_DB


class Tb_Strategy(Base_DB):
    """ 策略表
    `id` int NOT NULL AUTO_INCREMENT,
    `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '策略类型',
    `strategy_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '策略中文名',
    `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '策略文件名',
    `param_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    `is_baned` tinyint NULL DEFAULT -1 COMMENT '是否禁用 1 禁用 -1 不禁用',
    `note` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    """
    def __init__(self):
        __TB_NAME__ = 'tb_strategy'

    @classmethod
    def get_strategy_params(cls, cursor, strategy_type, strategy_name, **kwargs):
        """获取制定策略的相关参数
        """
        param_info_dic = {}
        sql = 'SELECT param_info, file_name FROM tb_strategy WHERE type=\'{}\' AND strategy_name=\'{}\';'.format(
            strategy_type, strategy_name
        )
        try:
            cursor.execute(sql)
            query_res = cursor.fetchone()
        except Exception as e:
            print('sql执行异常：', sql)
            query_res = None
        if(query_res):
            param_info_s = query_res[0]
            param_info_dic = json.loads(param_info_s)
        return param_info_dic

    @classmethod
    def push_strategy_params(cls, cursor, strategy_type, strategy_name, **kwargs):
        """更新设置策略相关参数"""
        result = False
        param_info = json.dumps(kwargs, ensure_ascii=False)
        sql = 'UPDATE tb_strategy SET param_info=\'{}\' WHERE type=\'{}\' AND strategy_name=\'{}\';'.format(
            param_info, strategy_type, strategy_name
        )
        try:
            cursor.execute(sql)
            result = True
        except Exception as e:
            print('sql执行异常：', sql)
        return result

    @classmethod
    def filter_strategy(cls, cursor, **kwargs):
        """筛选策略"""
        strategy_lis = []
        strategy_type = kwargs.get('strategy_type', '')
        is_baned = kwargs.get('is_baned', '')
        where_condition = ''
        if(strategy_type):
            where_condition = where_condition + ' AND ' + 'type=\'{}\''.format(
                strategy_type
            )
        if(is_baned):
            where_condition = where_condition + ' AND ' + 'is_baned=\'{}\''.format(
                is_baned
            )
        where_condition = where_condition.lstrip(' AND ')
        if(where_condition):
            sql = 'SELECT type, strategy_name, file_name, param_info, is_baned FROM tb_strategy WHERE {};'.format(
                where_condition
            )
        else:
            sql = 'SELECT type, strategy_name, file_name, param_info, is_baned FROM tb_strategy;'
        try:
            cursor.execute(sql)
            query_res = cursor.fetchall()
        except Exception as e:
            print('sql异常：', sql)
            query_res = None
        if(query_res):
            strategy_lis = query_res
        return strategy_lis
