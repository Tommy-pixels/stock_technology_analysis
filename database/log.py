"""
行为记录
"""
import json
from utils.common import Encode
from .base import Base_DB
import time


class Tb_Log(Base_DB):
    """ 记录
    `id` int NOT NULL,
    `operation_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `action` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `action_detail` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `action_status` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    `extra_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
    `create_time` datetime NULL DEFAULT NULL,
    `note` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
    """
    def __init__(self):
        __TB_NAME__ = 'tb_log'

    @classmethod
    def generate_operation_id(cls, name):
        operation_id = Encode.encodeByMd5(name + str(time.time()))
        return operation_id

    @classmethod
    def create_log(cls, cursor, operation_id, action, action_status, create_time, **kwargs):
        """创建记录
        :param excuting_file 执行文件
        """
        action_detail = kwargs.get('action_detail', '')
        note = kwargs.get('note', '')
        try:
            kwargs.pop('action_detail')
        except Exception as e:
            pass
        try:
            kwargs.pop('note')
        except Exception as e:
            pass
        extra_info = json.dumps(kwargs, ensure_ascii=False)
        sql = 'INSERT INTO tb_log (' \
              'operation_id, action, action_detail, action_status, extra_info, create_time, note) ' \
              'VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'.format(
            operation_id, action, action_detail, action_status, extra_info, create_time, note
        )
        result = False
        try:
            query_res = cursor.execute(sql)
            result = True
        except Exception as e:
            print('sql执行异常：', sql)
            query_res = -1
        return result


