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


async def main_loop():
    test_img = "../project/test_img/image4.jpg"
    with open(test_img, "rb") as img_f:
        image_data_t = img_f.read()
    flag_t =  await worker.async_interface_processing(
        _interface_name="add_photo",
        _user_id="test1",
        _suffix="jpg",
        _text="你好",
        _image_data=image_data_t
    )
    print(flag_t)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())
