# -*- coding: UTF-8 -*-


import os
import json
import traceback
import base64
import gzip
import pprint
import asyncio
from asyncio import events
import aiohttp
import async_timeout

from MainClass import MainClass

worker = MainClass()
worker.setup()


async def interface(path, user_id, image_data):
    return path, await worker.async_interface_processing(
                        _interface_name="add_face",
                        _user_id=user_id,
                        _suffix="bmp",
                        _image_data=image_data
                    )


async def main_loop():
    image_root = "/home/jerry/api_server/user_face_img"
    user_fom = "user_%d"
    path_user_id = dict()
    for path_t in range(500):
        user_t = user_fom % path_t
        if path_t >= 100:
            path_t = str(path_t)
        elif path_t >= 10:
            path_t = "0%d" % path_t
        else:
            path_t = "00%d" % path_t
        tmp_root = os.path.join(image_root, path_t)
        image_list = [os.path.join(tmp_root, f) for f in os.listdir(tmp_root) if os.path.isfile(os.path.join(tmp_root, f))]
        for img in image_list:
            path_user_id[img] = user_t
        
    max_request_count = 4
    tasks = list()
    finish_count = 0
    for path_t, user_t in path_user_id.items():
        print(path_t, user_t)
        try:
            with open(path_t, "rb") as img_f:
                image_data = img_f.read()
            ts = loop.create_task(
                interface(
                    path_t,
                    user_t,
                    image_data
                )
            )
            tasks.append(ts)
        except:
            print(traceback.format_exc())
            with open("rest_file", "a", encoding="utf-8") as rest_f:
                rest_f.write(path_t + "\n")
        try:
            if len(tasks) >= max_request_count:
                done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for d_t in done:
                    p_t, resp = d_t.result()
                    if resp:
                        finish_count += 1
                    else:
                        with open("rest_file", "a", encoding="utf-8") as rest_f:
                            rest_f.write(p_t + "\n")
                tasks = list(tasks)
        except:
            print(traceback.format_exc())
            pass
    print(finish_count)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())
