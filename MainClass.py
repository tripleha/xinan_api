# -*- coding:utf-8 -*-


import asyncio

from Config import Config_g
from DBManager import (
    DBTools,
    UserDBManager,
    ImageDBManager,
    AlbumDBManager
)
from APIProcess import APIProcessMain


class MainClass:
    """
    各模块集成控制类
    """

    def __init__(self):
        # 数据库管理模块
        self.db_tools = DBTools(
            _host=Config_g.get("mongodb", "host"),
            _port=Config_g.getint("mongodb", "port"),
            _db_name=Config_g.get("mongodb", "db_name")
        )
        # 后台功能接口调用管理模块
        self.api_process = APIProcessMain()
        # 用户信息和会话数据库管理模块
        self.user_db = UserDBManager(self.db_tools)
        # 图像数据库管理模块
        self.image_db = ImageDBManager(self.db_tools)
        # 相册人脸库数据库管理模块
        self.album_db = AlbumDBManager(self.db_tools, self.image_db, self.user_db, self.api_process)

        # 各模块的阻塞式调用接口注册
        self.interface = {
            "None": None,
        }
        # 各模块的非阻塞式接口注册
        self.async_interface = {
            "logout": self.user_db.session_close,
            "sign_up": self.user_db.create_user,
            "get_user_info": self.user_db.get_user_info,
            "update_user_info": self.user_db.update_user_info,
            "update_user_pwd": self.user_db.update_user_pwd,
            "login": self.user_db.add_login_session,
            "get_image": self.image_db.get_image,
            "add_photo": self.album_db.add_photo,
            "ensure_privacy_loc": self.album_db.ensure_privacy_loc,
            "delete_photo": self.album_db.delete_photo,
            "get_album": self.album_db.get_user_album,
            "add_face": self.album_db.add_face,
            "delete_face": self.album_db.delete_face,
            "get_faces": self.album_db.get_user_faces,
        }

    def setup(self):
        """
        各模块预启动控制，负责调用各模块的预启动方法
        """
        print("Server start!")

    async def check_token(self, session_id):
        """
        专门用于检查token合法性接口, 并根据token返回对应userID
        """
        return await self.user_db.check_session_valid(session_id)

    def interface_processing(self, _interface_name, **kwargs):
        """
        阻塞式接口统一调用，检错暂未添加
        接受参数
            _interface_name 为 要调用的接口名称，具体查询本类的成员变量interface
            **kwargs 包含所有要调用接口所接受的参数，调用需查看相关接口说明确定参数
        返回接口调用的结果
        """
        # TODO 统一检查传入参数的合法性
        interface_func_t = self.interface[_interface_name]
        return interface_func_t(**kwargs)

    async def async_interface_processing(self, _interface_name, **kwargs):
        """
        非阻塞式接口统一调用，检错暂未添加
        接受参数
            _interface_name 为 要调用的接口名称，具体查询本类的成员变量interface
            **kwargs 包含所有要调用接口所接受的参数，调用需查看相关接口说明确定参数
        返回接口调用的结果
        """
        # TODO 统一检查传入参数的合法性
        interface_func_t = self.async_interface[_interface_name]
        return await interface_func_t(**kwargs)


if __name__ == "__main__":
    pass
