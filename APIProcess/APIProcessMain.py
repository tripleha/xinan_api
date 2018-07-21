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
            "ocr": Config_g.get("api", "ocr"),
            "text": Config_g.get("api", "text"),
            "face_code": Config_g.get("api", "face_code"),
            "face_predict": Config_g.get("api", "face_predict"),
            "scene": Config_g.get("api", "scene"),
        }
        self.session = aiohttp.ClientSession()

        self.model_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "model_file"))
        try:
            if not os.path.isdir(self.model_path):
                os.makedirs(self.model_path)
        except:
            pass
        self.model_file = os.path.join(self.model_path, Config_g.get("api", "model_path"))
        print(self.model_file)

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

    async def text_detect(self, _image_path, _user_setting, _context_fenci, _context_pos, _context, _object_box, _class_name):
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

    async def face_get_code(self, _image_path):
        """
        获取人脸的图片的计算编码
        """
        url = self.api_url["face_code"]
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
                            return result_t["face_code"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None

    async def face_predict(self, _image_path):
        """
        获取图片关于人脸的信息
        """
        url = self.api_url["face_predict"]
        post_data_t = {
            "path": _image_path,
            "model_path": self.model_file,
        }
        r_t = 0
        while r_t <= 5:
            try:
                async with async_timeout.timeout(60):
                    async with self.session.post(url, data=json.dumps(post_data_t)) as resp:
                        resp_content = await resp.read()
                        result_t = json.loads(resp_content)
                        if result_t["code"] == 1:
                            return result_t["match_names"], result_t["match_locs"], result_t["name_to_loc"], result_t["face_locations"]
                        else:
                            return None, None, None, None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None, None, None, None

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
                            return result_t["result"]
                        else:
                            return None
            except:
                print(traceback.format_exc())
                r_t += 1
        return None


if __name__ == "__main__":
    pass
