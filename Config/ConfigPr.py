# -*- coding:utf-8 -*-
"""
Config控制
"""


import os
from configparser import ConfigParser


CONFIG_ROOT = os.path.dirname(__file__)


class ConfigPr(ConfigParser):
    """
    Config控制接口
    """
    def __init__(self):
        ConfigParser.__init__(self)
        # 因为第一次是在MainClass里调用，所以系统路径是在上层目录中
        self.read(os.path.join(CONFIG_ROOT, "config.ini"), encoding="utf-8")


Config_g = ConfigPr()


if __name__ == "__main__":
    print(Config_g.sections())