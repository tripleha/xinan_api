# -*- coding: utf-8 -*-
"""
图片相关数据库管理
"""


import time
import traceback
from bson.int64 import Int64
from bson.objectid import ObjectId
from bson.binary import Binary

from . import Config_g


class ImageDBManager:
    """
    图片管理数据库接口类
    """

    def __init__(self, _db_tools):
        self.db_tools = _db_tools
        self.image_coll = Config_g.get("mongodb", "image_coll")

        self.db_tools.add_collection(self.image_coll)

    def get_user_face(self, _user_id):
        """
        获取用户人脸数据的迭代器
        """
        index_t = {
            "userID": _user_id,
            "type": "face",
        }
        return self.db_tools.find(self.image_coll, index_t)

    async def insert_image(self, _user_id, _type, _suffix, _image_data):
        """
        将图片数据及信息插入数据库
        """
        insert_t = {
            "userID": _user_id,
            "type": _type,
            "suffix": _suffix,
            "content": Binary(_image_data),
            "date": Int64(int(time.time()*1000))
        }
        result_t = await self.db_tools.insert(self.image_coll, insert_t)
        if result_t.acknowledged and result_t.inserted_id is not None:
            return str(result_t.inserted_id)
        return 0

    async def delete_image(self, _user_id, _image_id):
        """
        删除图片信息和图片
        """
        if not ObjectId.is_valid(_image_id):
            return False
        index_t = {
            "_id": ObjectId(_image_id),
            "userID": _user_id
        }
        result_t = await self.db_tools.delete(self.image_coll, index_t)
        if result_t.acknowledged and result_t.deleted_count > 0:
            return True
        return False

    async def get_image(self, _user_id, _image_id):
        """
        唯一可以获取到图片数据的接口
        """
        if not ObjectId.is_valid(_image_id):
            return None
        index_t = {
            "_id": ObjectId(_image_id)
        }
        try:
            result_t = await self.db_tools.find(self.image_coll, index_t).limit(1).to_list(1)
            result_t = result_t[0]
            result_t["date"] = int(result_t["date"])
            result_t["content"] = bytes(result_t["content"])
            return result_t
        except:
            print(traceback.format_exc())
            return None


if __name__ == "__main__":
    pass
