import os
import sys

# 当前目录
basePath = os.path.abspath(os.path.dirname(__file__))
# 设置当前目录为执行运行目录
sys.path.append(basePath)

import configparser


class Config:
    """
    静态代码，类初始化的时候运行，对所有实例来说只运行一次
    """
    try:
        # 拼接获得config.ini路径
        __CONFIG_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
        __CONFIG_FILE_NAME = 'config.ini'
        # 读入配置文件
        __cf = configparser.RawConfigParser()
        __cf.read(os.path.join(__CONFIG_FILE_PATH, __CONFIG_FILE_NAME))
        print('读入config.ini配置：' + __cf.get('version', 'name'))
    except Exception as e:
        print("载入配置文件失败: " + os.path.join(__CONFIG_FILE_PATH, __CONFIG_FILE_NAME))
        print(e)
        raise e

    def get_value(self, section, option):
        try:
            value = self.__cf.get(section, option)
            return value
        except Exception as e:
            print("配置文件中没有该配置内容: section[" + section + "] option: " + option)
            raise e
