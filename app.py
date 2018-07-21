#! /usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
import asyncio
import time
import json
import traceback
import gzip
import base64

from apistar import ASyncApp, Route
from apistar import http

from MainClass import MainClass

worker = MainClass()
worker.setup()


async def sign_up(_query: http.Body) -> dict:
    result_t = {
        "code": 0,
    }
    try:
        query_t = json.loads(_query)
        flag_t = await worker.async_interface_processing(
            _interface_name="sign_up",
            _user_id=query_t["user_id"],
            _user_pwd=query_t["user_pwd"]
        )
        if flag_t:
            result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def login(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        token_t = await worker.async_interface_processing(
            _interface_name="login",
            _user_id=query_t["user_id"],
            _user_pwd=query_t["user_pwd"]
        )
        if token_t != "":
            result_t["code"] = 1
            result_t["token"] = token_t
    except:
        print(traceback.format_exc())
    return result_t


async def logout(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            flag_t = await worker.async_interface_processing(
                _interface_name="logout",
                _session_id=query_t["token"]
            )
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def get_user_info(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            user_info_t = await worker.async_interface_processing(
                _interface_name="get_user_info",
                _user_id=user_id_t
            )
            if user_info_t:
                result_t["code"] = 1
                result_t["user"] = user_info_t
    except:
        print(traceback.format_exc())
    return result_t


async def update_user_info(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            flag_t = await worker.async_interface_processing(
                _interface_name="update_user_info",
                _user_id=user_id_t,
                _base_privacy=query_t.get("base_privacy"),
                _scene_privacy=query_t.get("scene_privacy"),
                _phone_num=query_t.get("phone_num"),
                _idcard_num=query_t.get("idcard_num")
            )
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def update_user_pwd(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            flag_t = await worker.async_interface_processing(
                _interface_name="update_user_pwd",
                _user_id=user_id_t,
                _user_old_pwd=query_t["old_pwd"],
                _user_new_pwd=query_t["new_pwd"]
            )
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def get_image(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            data_t = await worker.async_interface_processing(
                _interface_name="get_image",
                _user_id=user_id_t,
                _image_id=query_t["image_id"]
            )
            if data_t is not None:
                result_t["suffix"] = data_t["suffix"]
                image_content_t = gzip.compress(data_t["content"])
                image_content_t = base64.b64encode(image_content_t).decode("ascii")
                result_t["content"] = image_content_t
                result_t["date"] = data_t["date"]
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def add_photo(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            print("into photo", user_id_t)
            image_data_t = base64.b64decode(query_t["content"])
            image_data_t = gzip.decompress(image_data_t)
            r_t = await worker.async_interface_processing(
                _interface_name="add_photo",
                _user_id=user_id_t,
                _suffix=query_t["suffix"],
                _text=query_t["text"],
                _image_data=image_data_t
            )
            if r_t:
                result_t["imageID"] = r_t["imageID"]
                result_t["face_to_loc"] = r_t["face_to_loc"]
                result_t["privacy_loc"] = r_t["privacy_loc"]
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def ensure_ploc(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            flag_t = await worker.async_interface_processing(
                _interface_name="ensure_privacy_loc",
                _user_id=user_id_t,
                _image_id=query_t["image_id"],
                _privacy_index=query_t["index"]
            )
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def delete_photo(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            flag_t = await worker.async_interface_processing(
                _interface_name="delete_photo",
                _user_id=user_id_t,
                _image_id=query_t["image_id"]
            )
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def get_photos(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            list_t = await worker.async_interface_processing(
                _interface_name="get_album",
                _user_id=user_id_t,
                _begin_index=query_t["begin"],
                _limit=query_t["limit"]
            )
            if isinstance(list_t, list):
                result_t["code"] = 1
                result_t["photos"] = list_t
    except:
        print(traceback.format_exc())
    return result_t


async def add_face(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            print("into", user_id_t)
            image_data_t = base64.b64decode(query_t["content"])
            image_data_t = gzip.decompress(image_data_t)
            flag_t = await worker.async_interface_processing(
                _interface_name="add_face",
                _user_id=user_id_t,
                _suffix=query_t["suffix"],
                _image_data=image_data_t
            )
            print(flag_t)
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def delete_face(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            flag_t = await worker.async_interface_processing(
                _interface_name="delete_face",
                _user_id=user_id_t,
                _image_id=query_t["image_id"]
            )
            if flag_t:
                result_t["code"] = 1
    except:
        print(traceback.format_exc())
    return result_t


async def get_faces(_query: http.Body) -> dict:
    result_t = {
        "code": 0
    }
    try:
        query_t = json.loads(_query)
        user_id_t = await worker.check_token(query_t["token"])
        if user_id_t:
            list_t = await worker.async_interface_processing(
                _interface_name="get_faces",
                _user_id=user_id_t
            )
            if isinstance(list_t, list):
                result_t["code"] = 1
                result_t["faces"] = list_t
    except:
        print(traceback.format_exc())
    return result_t


routes = [
    Route("/signup", method="POST", handler=sign_up),
    Route("/login", method="POST", handler=login),
    Route("/logout", method="POST", handler=logout),
    Route("/getuserinfo", method="POST", handler=get_user_info),
    Route("/changeuserinfo", method="POST", handler=update_user_info),
    Route("/changeuserpwd", method="POST", handler=update_user_pwd),
    Route("/getimage", method="POST", handler=get_image),
    Route("/addphoto", method="POST", handler=add_photo),
    Route("/ensureprivacyloc", method="POST", handler=ensure_ploc),
    Route("/deletephoto", method="POST", handler=delete_photo),
    Route("/getphotos", method="POST", handler=get_photos),
    Route("/addface", method="POST", handler=add_face),
    Route("/deleteface", method="POST", handler=delete_face),
    Route("/getfaces", method="POST", handler=get_faces),
]


APP = ASyncApp(routes=routes)


if __name__ == "__main__":
    pass
