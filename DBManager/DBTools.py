# -*- coding:utf-8 -*-
"""
数据库调用封装
"""


import motor
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo

from . import Config_g


class DBTools:
    """
    数据库操作类
    """

    def __init__(self, _host, _port, _db_name):
        self.host = _host
        self.port = _port
        self.db_name = _db_name
        self.client = AsyncIOMotorClient(host=_host, port=_port)
        self.manage_db = self.client[self.db_name]
        self.collections = dict()

    def add_collection(self, _coll):
        """
        注册collection实例的接口
        接受参数
            _coll 为 集合的名字
        """
        self.collections[_coll] = self.manage_db[_coll]

    def find(self, _coll, _condition, _sort=None, _limit=0):
        """
        查询接口

        I/O 并不在该调用发生，而是在遍历Cursor的时候发生，所以不用加入async

        接受参数
            _coll 为 查询集合的名字
            _condition 为 一个字典，要查询的条件情况
            _sort 为 一个代表排序情况的列表（可选
                如：[("date", pymongo.ASCENDING),] 表示结果按照date升序排序
            _limit 为 可以返回的最大结果个数（可选
        返回一个类似迭代器的东西
        """
        if _sort is None and _limit == 0:
            return self.collections[_coll].find(_condition)
        elif _sort is not None and _limit == 0:
            return self.collections[_coll].find(_condition, sort=_sort)
        elif _sort is None and _limit != 0:
            return self.collections[_coll].find(_condition, limit=_limit)
        elif _sort is not None and _limit != 0:
            return self.collections[_coll].find(_condition, sort=_sort, limit=_limit)

    async def insert(self, _coll, _data):
        """
        插入数据接口，检错暂未添加
        不提供多条插入的接口，统一使用单条插入
        接受参数
            _coll 为 查询集合的名字
            _data 为 一个字典 即要插入的数据
        返回结果
            返回的是一个mongodb的操作结果集
            有以下键值
                acknowledged 在 使用其他键值之前必须检查其是否为True，否则会产生错误
                inserted_id 操作插入的数据的_id字段信息
        """
        coll_t = self.collections[_coll]
        return await coll_t.insert_one(_data)

    async def upsert(self, _coll, _condition, _data, _upsert=True):
        """
        更新或插入数据接口，检错暂未添加
        不提供多条版本，统一使用单条操作
        接受参数
            _coll 为 操作集合的名字
            _condition 为 一个字典，要查询的条件情况
                满足条件的第一个数据(按插入数据库先后排序)会被更新
                若没有满足要求的数据，则进行插入操作
            _data 为 一个字典 即要进行的改变操作
            _upsert 为 布尔变量，表示是否可以执行插入操作
        返回结果
            返回的是一个mongodb的操作结果集
            有以下键值
                acknowledged 在 使用其他键值之前必须检查其是否为True，否则会产生错误
                matched_count 匹配的结果数目
                modified_count 更改的结果数目
                raw_result mongo服务返回的原始结果
                upserted_id 操作改变的数据的_id字段信息
        """
        coll_t = self.collections[_coll]
        return await coll_t.update_one(_condition, _data, upsert=_upsert)

    async def delete(self, _coll, _condition):
        """
        删除数据库文档接口，检错暂未添加
        不提供多条版本，统一使用单条操作
        接受参数
            _coll 为 操作集合的名字
            _condition 为 一个字典，要删除文档的索引条件
        返回结果
            返回的是一个mongodb的操作结果集
            有以下键值
                acknowledged 在 使用其他键值之前必须检查其是否为True，否则会产生错误
                deleted_count 删除的文档的数目
                raw_result mongo服务返回的原始结果
        """
        coll_t = self.collections[_coll]
        return await coll_t.delete_one(_condition)

    async def find_one_and_update(self, _coll, _condition, _data, _fields, _upsert=True):
        """
        为进行findAndModify的原子性操作而设立的接口，检错有待完善
        该接口可用于自增字段的控制使用
        若需要返回结果的特定字段也可使用该接口
        该接口最多可改变一个文档
        一般插入和更新操作使用 update_or_insert 效率较高(有待证实)(因为可能不需要返回额外信息)
        接受参数
            _coll 为 操作集合的名字
            _condition 为 要查询的条件，必须确保该条件能够查询到的数据在集合中是唯一的
                否则这次操作就非原子性操作了
            _data 为 一个字典 要进行的修改操作
            _fields 为 一个列表 即更新后的文档中要返回的字段
            _upsert 为 布尔变量，表示是否可以执行插入操作
        返回结果
            返回一个字典，包含了参数中需要返回的字段的结果
            若_upsert设置为False，则当_condition不能找到目标文档时会返回None
        """
        # 处理返回字段列表
        projection_t = {
            "_id": False,
        }
        for field_t in _fields:
            projection_t[field_t] = True
        coll_t = self.collections[_coll]
        return await coll_t.find_one_and_update(
            _condition, _data, projection=projection_t, upsert=_upsert,
            return_document=pymongo.ReturnDocument.AFTER
        )


if __name__ == "__main__":
    pass
