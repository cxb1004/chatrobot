import os
import sys

basePath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basePath)

import configparser


class Config:
    try:
        __CONFIG_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
        __CONFIG_FILE_NAME = 'config.ini'
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
