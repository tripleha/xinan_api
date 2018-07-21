# -*- coding: utf-8 -*-
"""
User信息数据库管理
"""

import time
import traceback
from bson.int64 import Int64
from bson.objectid import ObjectId

from . import Config_g


class UserDBManager:
    """
    User信息数据库管理类
    """

    def __init__(self, _db_tools):
        self.db_tools = _db_tools
        self.user_coll = Config_g.get("mongodb", "user_coll")
        self.session_coll = Config_g.get("mongodb", "session_coll")

        self.db_tools.add_collection(self.user_coll)
        self.db_tools.add_collection(self.session_coll)

        self.session_valid_time = 3600*24*7
        self.base_privacy_list = (
            "address",
            "phone",
            "bankcard",
            "car_number",
            "org",
            "email",
            "idcard",
            "time",
            "url",
            "name",
            "stucard",
            "contract",
            "business_licence",
            "serial_number",
            "face",
        )
        self.scene_privacy_list = (
            "bedroom",
            "chemistry_lab",
            "conference_center",
            "conference_room",
            "office_cubicles",
            "airport_terminal",
            "bank_vault",
            "banquet_hall",
            "bathroom",
            "biology_laboratory",
            "childs_room",
            "dining_hall",
            "dining_room",
            "dorm_room",
            "dressing_room",
            "embassy",
            "gymnasium",
            "home_office",
            "hospital_room",
            "legislative_chamber",
            "physics_laboratory",
            "restaurant",
            "server_room",
        )

    async def create_user(self, _user_id, _user_pwd):
        """
        在数据库中创建用户数据
        """
        index_t = {
            "userID": _user_id,
        }
        insert_t = {
            "$setOnInsert": {
                "userPWD": _user_pwd,
                # 设置默认的权限数值
                "base_privacy": list(),
                "scene_privacy": list(),
                "phone_num": "",
                "idcard_num": "",
            }
        }
        result_t = await self.db_tools.upsert(self.user_coll, index_t, insert_t)
        if result_t.acknowledged and result_t.upserted_id is not None:
            return True
        else:
            return False

    async def check_user_pwd(self, _user_id, _user_pwd):
        """
        检查用户的密码是否正确
        """
        index_t = {
            "userID": _user_id,
            "userPWD": _user_pwd,
        }
        result_t = await self.db_tools.find(self.user_coll, index_t).count()
        if result_t > 0:
            return True
        else:
            return False

    async def get_user_info(self, _user_id):
        """
        获取用户信息
        """
        index_t = {
            "userID": _user_id,
        }
        try:
            result_t = await self.db_tools.find(self.user_coll, index_t).limit(1).to_list(1)
            result_t = result_t[0]
            result_t.pop("_id")
            result_t.pop("userPWD")
            return result_t
        except:
            return False

    async def get_user_privacy_setting(self, _user_id):
        """
        获取用户隐私设置信息
        """
        user_info_t = await self.get_user_info(_user_id)
        user_privacy_t = dict()
        if user_info_t:
            for privacy_t in self.base_privacy_list:
                if privacy_t in user_info_t["base_privacy"]:
                    user_privacy_t[privacy_t] = True
                else:
                    user_privacy_t[privacy_t] = False
            user_privacy_t["scene_privacy"] = user_info_t["scene_privacy"]
            return user_privacy_t
        return False

    def detect_scene_privacy(self, scene_result, scene_privacy):
        """
        获取当前的用户关注的场景信息
        """
        for scene in scene_result:
            if scene in self.scene_privacy_list and scene_result[scene] > 0.2:
                return scene
        return False

    async def find_user_has_face(self, _user_ids):
        """
        获取用户中设置了人脸隐私的用户
        """
        if len(_user_ids) == 0:
            return list()
        index_t = {
            "userID": {"$in": _user_ids},
            "base_privacy": "face",
        }
        r_t = await self.db_tools.find(self.user_coll, index_t).to_list(len(_user_ids))
        result_t = [user_t["userID"] for user_t in r_t]
        return result_t

    async def update_user_pwd(self, _user_id, _user_old_pwd, _user_new_pwd):
        """
        更改用户密码
        """
        index_t = {
            "userID": _user_id,
            "userPWD": _user_old_pwd,
        }
        update_t = {
            "$set": {
                "userPWD": _user_new_pwd,
            }
        }
        result_t = await self.db_tools.upsert(self.user_coll, index_t, update_t, _upsert=False)
        if result_t.acknowledged and result_t.matched_count > 0:
            return True
        else:
            return False

    async def update_user_info(self, _user_id, _base_privacy=None, _scene_privacy=None, _phone_num=None, _idcard_num=None):
        """
        更改用户信息
        """
        index_t = {
            "userID": _user_id,
        }
        update_t = {
            "$set": dict()
        }
        if isinstance(_base_privacy, list):
            for privacy_t in _base_privacy:
                if privacy_t not in self.base_privacy_list:
                    return False
            update_t["$set"]["base_privacy"] = _base_privacy
        if isinstance(_scene_privacy, list):
            for privacy_t in _scene_privacy:
                if privacy_t not in self.scene_privacy_list:
                    return False
            update_t["$set"]["scene_privacy"] = _scene_privacy
        if isinstance(_phone_num, str):
            update_t["$set"]["phone_num"] = _phone_num
        if isinstance(_idcard_num, str):
            update_t["$set"]["idcard_num"] = _idcard_num
        result_t = await self.db_tools.upsert(self.user_coll, index_t, update_t, _upsert=False)
        if result_t.acknowledged and result_t.matched_count > 0:
            return True
        else:
            return False

    async def add_login_session(self, _user_id, _user_pwd):
        """
        用户登录，添加对应session，并返回sessionid
        """
        if await self.check_user_pwd(_user_id, _user_pwd):
            insert_t = {
                "userID": _user_id,
                "valid": Int64(int((time.time()+self.session_valid_time)*1000)),
            }
            result_t = await self.db_tools.insert(self.session_coll, insert_t)
            if result_t.acknowledged and result_t.inserted_id is not None:
                session_id = str(result_t.inserted_id)
                return session_id
            else:
                return ""
        else:
            return ""

    async def session_close(self, _session_id):
        """
        用户退出登录，清除相关session
        """
        if ObjectId.is_valid(_session_id):
            index_t = {
                "_id": ObjectId(_session_id),
            }
            result_t = await self.db_tools.delete(self.user_coll, index_t)
            if result_t.acknowledged and result_t.deleted_count > 0:
                return True
            else:
                return False
        else:
            return False

    async def check_session_valid(self, _session_id):
        """
        检查用户的sessionid是否合法，并返回对应userID
        """
        if ObjectId.is_valid(_session_id):
            index_t = {
                "_id": ObjectId(_session_id),
            }
            try:
                result_t = await self.db_tools.find(self.session_coll, index_t).limit(1).to_list(1)
                result_t = result_t[0]
                return result_t["userID"]
            except:
                return False
        else:
            return False


if __name__ == "__main__":
    pass
