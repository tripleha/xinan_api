# -*- coding: utf-8 -*-
"""
API接口调用管理
"""


import os
import json
import asyncio
import traceback
from asyncio import events
import aiohttp
import async_timeout

from . import Config_g


class APIProcessMain:
    """
    API接口调用类
    """

    def __init__(self):
        self.api_url = {
            "object": Config_g.get("api", "object"),
            "baidu_object": Config_g.get("api", "baidu_object"),
            "ocr": Config_g.get("api", "ocr"),
            "text": Config_g.get("api", "text"),
            "privacy_degree": Config_g.get("api", "privacy_degree"),
            "add_face": Config_g.get("api", "add_face"),
            "delete_face": Config_g.get("api", "delete_face"),
            "get_face": Config_g.get("api", "get_face"),
            "face_predict": Config_g.get("api", "face_predict"),
            "scene": Config_g.get("api", "scene"),
        }
        self.session = aiohttp.ClientSession()

    async def object_detect(self, _image_path):
        """
        物体检测API接口
        """
        url = self.api_url["object"]
        post_data_t = {
            "path": _image_path,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["box"], result_t["class"]
                        else:
                            return None, None
            except:
                print(traceback.format_exc())
                r_t += 1        
        return None, None

    async def object_baidu(self, _image_path):
        """
        百度的物体检测API接口
        """
        url = self.api_url["baidu_object"]
        post_data_t = {
            "path": _image_path,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["ob_class"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1        
        return None

    async def ocr_detect(self, _image_path):
        """
        文字识别API接口
        """
        url = self.api_url["ocr"]
        post_data_t = {
            "path": _image_path,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["context_fenci"], result_t["context_pos"], result_t["context"]
                        else:
                            return None, None, None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None, None, None

    async def text_detect(self, _image_path, _user_setting, _context_fenci, _context_pos, _context, _object_box, _class_name, _object_class):
        """
        文字隐私校验API接口
        """
        url = self.api_url["text"]
        post_data_t = {
            "path": _image_path,
            "user_setting": _user_setting,
            "context_fenci": _context_fenci,
            "context_pos": _context_pos,
            "context": _context,
            "object_box": _object_box,
            "class_name": _class_name,
            "object_class": _object_class,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["all_locs"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None

    async def add_face(self, _image_path, _user_id):
        """
        向百度人脸库添加人脸
        """
        url = self.api_url["add_face"]
        post_data_t = {
            "path": _image_path,
            "user_id": _user_id,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["token"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None

    async def delete_face(self, _image_token, _user_id):
        """
        从百度人脸库删除人脸
        """
        url = self.api_url["delete_face"]
        post_data_t = {
            "token": _image_token,
            "user_id": _user_id,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return True
                        else:
                            return False
            except:
                print(traceback.format_exc())
                r_t += 1
        return False

    async def get_face(self, _image_path):
        """
        百度人脸检测API
        """
        url = self.api_url["get_face"]
        post_data_t = {
            "path": _image_path,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return True
                        else:
                            return False
            except:
                print(traceback.format_exc())
                r_t += 1
        return False

    async def face_predict(self, _image_path):
        """
        获取图片关于人脸的信息
        """
        url = self.api_url["face_predict"]
        post_data_t = {
            "path": _image_path,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["user_loc"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None

    async def scene_detect(self, _image_path):
        """
        获取图片关于场景的信息
        """
        url = self.api_url["scene"]
        post_data_t = {
            "path": _image_path
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["environment_type"], result_t["scene_class"], result_t["scene_event"]
                        else:
                            return None, None, None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None, None, None

    async def privacy_degree(self, _features):
        """
        获取图片隐私评分
        """
        url = self.api_url["privacy_degree"]
        post_data_t = {
            "features": _features
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["score"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None


if __name__ == "__main__":
    pass
