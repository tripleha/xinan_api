# -*- coding: utf-8 -*-
"""
相册信息数据库管理
"""

import os
import time
import asyncio
from asyncio import events
from bson.int64 import Int64
import pymongo
import pprint

from . import Config_g


class AlbumDBManager:
    """
    相册信息数据库管理类
    """

    def __init__(self, _db_tools, _image_manager, _user_manager, _api_process):
        self.db_tools = _db_tools
        self.image_manager = _image_manager
        self.user_manager = _user_manager
        self.api_process = _api_process
        self.album_coll = Config_g.get("mongodb", "album_coll")
        self.face_coll = Config_g.get("mongodb", "face_coll")
        self.inc_coll = Config_g.get("mongodb", "inc_coll")

        self.db_tools.add_collection(self.album_coll)
        self.db_tools.add_collection(self.face_coll)
        self.db_tools.add_collection(self.inc_coll)

        self.tmp_file_path = os.path.join(os.path.dirname(__file__), "..", "tmp_file")

        try:
            if not os.path.isdir(self.tmp_file_path):
                os.makedirs(self.tmp_file_path)
        except:
            pass

    async def inc_tmp_image_id(self):
        """
        临时文件的编号，采用自增字段，则每个ID只能使用一次
        在维护时复位该文档的nextID就能实现临时文件ID重用
        """
        result_t = await self.db_tools.find_one_and_update(
            self.inc_coll,
            {
                "type": "tmp_file_id",
            },
            {
                "$inc": {"nextID": 1},
            },
            ["nextID",]
        )
        return str(result_t["nextID"])

    async def add_photo(self, _user_id, _suffix, _text, _image_data):
        """
        向用户相册添加照片
        """
        start_t = time.time()
        # 获取用户隐私设置
        user_privacy_t = await self.user_manager.get_user_privacy_setting(_user_id)
        if not user_privacy_t:
            return False
        print(user_privacy_t)
        # 生成临时文件
        tmp_img_id = await self.inc_tmp_image_id()
        tmp_img_path = os.path.abspath(os.path.join(self.tmp_file_path, tmp_img_id))
        with open(tmp_img_path, "wb") as tmp_f:
            tmp_f.write(_image_data)
        # API调用
        loop = events.get_event_loop()
        object_task = loop.create_task(self.api_process.object_detect(tmp_img_path))
        ob_baidu_task = loop.create_task(self.api_process.object_baidu(tmp_img_path))
        ocr_task = loop.create_task(self.api_process.ocr_detect(tmp_img_path))
        face_task = loop.create_task(self.api_process.face_predict(tmp_img_path))
        get_face_task = loop.create_task(self.api_process.get_face(tmp_img_path))
        scene_task = loop.create_task(self.api_process.scene_detect(tmp_img_path))
        await asyncio.wait([object_task, ob_baidu_task, ocr_task, get_face_task, scene_task,], return_when=asyncio.ALL_COMPLETED)
        context_fenci_t, context_pos_t, context_t, chars_pos_t = ocr_task.result()
        object_box_t, object_name_t = object_task.result()
        ob_class_t = ob_baidu_task.result()
        face_flag_t = get_face_task.result()
        environment_type_t, scene_class_t, scene_event_t = scene_task.result()
        if object_box_t is None or context_fenci_t is None or ob_class_t is None or environment_type_t is None:
            # 接口调用失败，退出
            os.remove(tmp_img_path)
            return False
        # scene_t = self.user_manager.detect_scene_privacy(scene_class_t, user_privacy_t["scene_privacy"])
        features_t = [list(), list(), list(), face_flag_t]
        features_t[0].extend(ob_class_t)
        features_t[1].extend(ob_class_t)
        features_t[1].extend(scene_event_t)
        features_t[2].extend(ob_class_t)
        features_t[2].extend(object_name_t)
        # scene_name_t = ""
        if scene_class_t:
            # scene_name_t = scene_t
            features_t[0].extend(scene_class_t)
        privacy_task = loop.create_task(self.api_process.privacy_degree(features_t))
        if context_fenci_t:
            text_task = loop.create_task(self.api_process.text_detect(
                tmp_img_path,
                user_privacy_t,
                context_fenci_t,
                context_pos_t,
                context_t,
                chars_pos_t,
                object_box_t,
                object_name_t,
                ob_class_t
            ))
            await asyncio.wait([face_task, privacy_task, text_task,], return_when=asyncio.ALL_COMPLETED)
            all_locs_t, num_loc_t = text_task.result()
            if num_loc_t:
                privacy_num_list_t = await self.user_manager.find_num_in_user(num_loc_t.keys())
                print("privacy_num_list_t")
                print(privacy_num_list_t)
                privacy_num_locs_t = [num_loc_t[num_t] for num_t in num_loc_t if num_t in privacy_num_list_t]
                for nloc_t in privacy_num_locs_t:
                    if nloc_t in all_locs_t:
                        all_locs_t.remove(nloc_t)
            else:
                privacy_num_locs_t = list()
        else:
            await asyncio.wait([face_task, privacy_task,], return_when=asyncio.ALL_COMPLETED)
            all_locs_t = list()
            privacy_num_locs_t = list()
        user_loc_t = face_task.result()
        score_t = privacy_task.result()
        if all_locs_t is None or user_loc_t is None or score_t is None:
            # 接口调用失败，退出
            os.remove(tmp_img_path)
            return False
        print("context_fenci_t")
        pprint.pprint(context_fenci_t)
        print("context_pos_t")
        pprint.pprint(context_pos_t)
        print("context_t")
        pprint.pprint(context_t)
        print("chars_pos_t")
        pprint.pprint(chars_pos_t)
        print("all_locs_t")
        pprint.pprint(all_locs_t)
        print("privacy_num_locs_t")
        pprint.pprint(privacy_num_locs_t)
        print("user_loc_t")
        pprint.pprint(user_loc_t)
        print("scene_class_t")
        print(scene_class_t)
        print("score_t")
        print(score_t)
        # 删除临时文件
        os.remove(tmp_img_path)

        done_faces_t = list()
        face_users = list()
        if isinstance(user_loc_t, dict) and len(user_loc_t) > 0:
            get_user_t = list(user_loc_t.keys())
            if _user_id in get_user_t:
                get_user_t.remove(_user_id)
            face_users = await self.user_manager.find_user_has_face(get_user_t)
            for f_user_t in face_users:
                done_faces_t.append(user_loc_t[f_user_t])
        
        privacy_loc_dict_t = dict()
        for p_index_t, loc_t in enumerate(all_locs_t, 0):
            privacy_loc_dict_t[str(p_index_t)] = loc_t

        img_id_t = await self.image_manager.insert_image(_user_id, "album", _suffix, _image_data)
        if img_id_t == 0:
            print("ins fail")
            return False
        insert_t = {
            "userID": _user_id,
            "text": _text,
            "imageID": img_id_t,
            "face_loc": user_loc_t,
            "face_users": face_users,
            "privacy_loc": privacy_loc_dict_t,
            "privacy_index": list(),
            "privacy_num_loc": privacy_num_locs_t,
            "scene": scene_class_t,
            "score": score_t,
            "date": Int64(int(time.time()*1000))
        }
        result_t = await self.db_tools.insert(self.album_coll, insert_t)
        if result_t.acknowledged and result_t.inserted_id is not None:
            end_t = time.time() - start_t
            print("success use %.6f" % end_t)
            return {
                "imageID": img_id_t,
                "face_to_loc": done_faces_t,
                "privacy_loc": privacy_loc_dict_t,
                "privacy_num_loc": privacy_num_locs_t,
                "scene": scene_class_t,
                "score": score_t,
            }
        print("inss fail")
        return False

    async def ensure_privacy_loc(self, _user_id, _image_id, _privacy_index):
        """
        用户选定内容隐私框
        """
        if not isinstance(_privacy_index, list):
            return False
        index_t = {
            "userID": _user_id,
            "imageID": _image_id,
        }
        update_t = {
            "$set": {
                "privacy_index": _privacy_index,
            }
        }
        result_t = await self.db_tools.upsert(
            self.album_coll, index_t, update_t, _upsert=False)
        if result_t.acknowledged and result_t.matched_count > 0:
            return True
        return False

    async def delete_photo(self, _user_id, _image_id):
        """
        删除相册照片
        """
        await self.image_manager.delete_image(_user_id, _image_id)
        index_t = {
            "userID": _user_id,
            "imageID": _image_id,
        }
        result_t = await self.db_tools.delete(self.album_coll, index_t)
        if result_t.acknowledged and result_t.deleted_count > 0:
            return True
        return False

    async def get_user_album(self, _user_id, _begin_index, _limit):
        """
        获取相册的照片信息
        """
        index_t = {
            "userID": _user_id,
        }
        sort_t = [("date", pymongo.ASCENDING),]
        iter_t = self.db_tools.find(self.album_coll, index_t, _sort=sort_t).limit(_limit).skip(_begin_index)
        result_t = await iter_t.to_list(_limit)
        return_t = list()
        for img_t in result_t:
            into_t = {
                "imageID": img_t["imageID"],
                "privacy_index": img_t["privacy_index"],
                "privacy_loc": img_t["privacy_loc"],
                "privacy_num_loc": img_t["privacy_num_loc"],
                "text": img_t["text"],
                "face_to_loc": list(),
                "scene": img_t["scene"],
                "score": img_t["score"],
                "date": int(img_t["date"])
            }
            for f_user_t in img_t["face_users"]:
                into_t["face_to_loc"].append(img_t["face_loc"][f_user_t])
            return_t.append(into_t)
        return return_t

    async def add_face(self, _user_id, _suffix, _image_data):
        """
        向数据库中添加用户人脸数据
        """
        face_count = await self.image_manager.get_user_face(_user_id).count()
        if face_count > 5:
            return False
        # 生成临时文件
        tmp_img_id = await self.inc_tmp_image_id()
        tmp_img_path = os.path.abspath(os.path.join(self.tmp_file_path, tmp_img_id))
        with open(tmp_img_path, "wb") as tmp_f:
            tmp_f.write(_image_data)
        token_t = await self.api_process.add_face(tmp_img_path, _user_id)
        if token_t is None:
            os.remove(tmp_img_path)
            return False
        # 删除临时文件
        os.remove(tmp_img_path)
        img_id_t = await self.image_manager.insert_image(_user_id, "face", _suffix, _image_data)
        if img_id_t == 0:
            return False
        insert_t = {
            "userID": _user_id,
            "imageID": img_id_t,
            "token": token_t,
            "date": Int64(int(time.time()*1000))
        }
        result_t = await self.db_tools.insert(self.face_coll, insert_t)
        if result_t.acknowledged and result_t.inserted_id is not None:
            return True
        return False

    async def delete_face(self, _user_id, _image_id):
        """
        删除人脸图片
        """
        index_t = {
            "userID": _user_id,
            "imageID": _image_id,
        }
        face_info_t = await self.db_tools.find(self.face_coll, index_t).to_list(10)
        face_token_t = face_info_t[0]["token"]
        state_t = await self.api_process.delete_face(face_token_t, _user_id)
        if not state_t:
            return False
        await self.image_manager.delete_image(_user_id, _image_id)
        result_t = await self.db_tools.delete(self.face_coll, index_t)
        if result_t.acknowledged and result_t.deleted_count > 0:
            return True
        return False

    async def get_user_faces(self, _user_id):
        """
        获取当前用户已经上传的人脸信息
        """
        index_t = {
            "userID": _user_id,
        }
        sort_t = [("date", pymongo.ASCENDING),]
        faces_list_t = await self.db_tools.find(self.face_coll, index_t, _sort=sort_t).to_list(10)
        result_t = [
            {
                "imageID": face_t["imageID"],
                "date": int(face_t["date"])
            } 
            for face_t in faces_list_t
        ]
        return result_t


if __name__ == "__main__":
    pass
