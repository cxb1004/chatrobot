# -*- ecoding: utf-8 -*-
# @Function: <自定义工具类>
# @Author: pkuokuo
# @Time: 2021/4/23

# 系统包
import os
import re
import shutil
import time
from flask_sqlalchemy import Model
import sqlalchemy
from datetime import datetime as cdatetime  # 有时候会返回datatime类型
from sqlalchemy import DateTime, Numeric, Date, Time  # 有时又是DateTime
from datetime import date as cdate, time as ctime

# 自定义包
from common.log import Log
log = Log()

class Utils(object):
    
    '将两个list的值相乘'
    def multiplyList(self, list1=None, list2=None):
        ret_list = []
        if isinstance(list1, list) and isinstance(list2, list):
            for i in range(len(list1)):
                try:
                    list1_value_float = float(list1[i])
                    list2_value_float = float(list2[i])
                    ret_list.append(list1_value_float * list2_value_float)
                except Exception as e:
                    log.error('utlis_multiplyList_e:{}'.format(str(e)))
                    return []
        return ret_list
    
    '对list值求和'
    def sumListIntValue(self, param_list=None):
        sum = 0
        if isinstance(param_list, list):
            for value in param_list:
                try:
                    value_int = int(value)
                    sum += value_int
                except Exception as e:
                    log.error('utils_sumListIntValue_e:{}'.format(str(e)))
                    return 0
        return sum


    '获取dict的value返回list'
    def dictIntValueToList(self, param_dict=None):
        ret_list = []
        if isinstance(param_dict, dict):
            for key, value in param_dict.items():
                try:
                    value_int = int(value)
                    ret_list.append(value_int)
                except Exception as e:
                    log.error('utils_dictIntValueToList_e:{}'.format(str(e)))
                    return []
        return ret_list

    # 读取文件内容
    def fileToList(self, filePath):
        with open(filePath, 'r', encoding='utf-8') as readFile:
            return readFile.read().splitlines()

    """判断字符是否为空"""
    def str_isNull(self, st):
        if st is None or st == '':
            return True
        return False

    # 关闭数据库连接
    def closeConn(self, conn=None):
        try:
            conn.close()
        except Exception as e:
            log.error('数据库关闭连接失败：{}'.format(str(e)))

    # 执行数据库操作
    def executeNoQuerySQL(self, conn=None, sql=None, params=None):
        trans = conn.begin()
        try:
            statement = sqlalchemy.text(sql)
            db_result = conn.execute(statement, params)
            trans.commit()
        except Exception as e:
            trans.rollback()
            log.error("数据库操作失败：%s" % e)



    # 执行数据库操作
    def executeSQL(self,conn=None,sql=None,params=None):
        data = []
        # trans = conn.begin()
        try:

            statement = sqlalchemy.text(sql)
            db_result = conn.execute(statement, params)

            # trans.commit()
            data = self.queryToDict(list(db_result))
        except Exception as e:
            # trans.rollback()
            log.error("数据库操作失败：%s" % e)
        finally:
            return data

    # 获取数据库连接
    def getcon(self,user=None,password=None,host=None,port=None,database=None,charset=None):
        conn = None
        try:
            engine = sqlalchemy.create_engine(
                "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (user, password, host, port, database, charset),
                max_overflow=10,
                echo=True
            )
            conn = engine.connect()
        except Exception as e:
            log.error('数据库连接获取失败：{}'.format(str(e)))
        finally:
            return conn

    def del_file(self, filePath):
        """
        如果文件夹存在，就删除文件夹下的所有文件
        :param filePath:
        :return:
        """
        if os.path.exists(filePath):
            for f in os.listdir(filePath):
                file_data = os.path.join(filePath, f)
                if os.path.isfile(file_data) == True:
                    os.remove(file_data)




    def removeFileIfExists(self, filePath):
        """
        如果文件已经存在，就删除文件
        :param filePath:
        :return:
        """
        if os.path.isfile(filePath):
            os.remove(filePath)


    def replaceMutiSpace(self, str):
        """
        多个空格替换成单个空格
        :param str:
        :return:
        """
        str = re.sub(' +', ' ', str)
        return str


    def remove53Emoji(self, str):
        """
        移除53自定义的表情符号
        :param str:
        :return:
        """
        patten = re.compile('{53b#\d*#}')
        str = re.sub(patten, '', str)
        return str


    def isFileExist(self, file):
        """
        判断文件是否存在
        :param file:
        :return:
        """
        if os.path.isfile(file):
            return True
        return False


    def file_size_format(self, file):
        size = os.path.getsize(file)
        if size < 1000:
            return '%i' % size + 'size'
        elif 1000 <= size < 1000000:
            return '%.1f' % float(size / 1000) + 'KB'
        elif 1000000 <= size < 1000000000:
            return '%.1f' % float(size / 1000000) + 'MB'
        elif 1000000000 <= size < 1000000000000:
            return '%.1f' % float(size / 1000000000) + 'GB'
        elif 1000000000000 <= size:
            return '%.1f' % float(size / 1000000000000) + 'TB'


    def file_update_time_format(self, file):
        mtime = os.stat(file).st_mtime
        file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        return file_modify_time


    def get_timestamp(self, format=None):
        t = time.time()
        if format is None:
            return t
        elif format == 's':
            # 返回秒级时间戳
            return int(t)
        elif format == 'ms':
            # 返回毫秒级时间戳
            return int(round(t * 1000))
        elif format == 'y-m-dhms':
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        elif format == 'y-m-d':
            return time.strftime("%Y-%m-%d", time.localtime(t))
        elif format == 'ymd':
            return time.strftime("%Y%m%d", time.localtime(t))
        elif format == 'ymdhms':
            return time.strftime("%Y%m%d%H%M%S", time.localtime(t))


    def copyFile(self, file=None, path=None, is_overwrite=False):
        # 检查待复制的文件是否存在
        if not self.isFileExist(file):
            raise Exception('待复制的文件不存在！')

        # 获得相同的文件名
        file_name = os.path.basename(file)
        target_file = os.path.join(path, file_name)

        # 判断目标文件是否存在
        if self.isFileExist(target_file):
            if is_overwrite:
                # 如果允许覆盖，就执行覆盖操作（先删除，后复制）
                self.removeFileIfExists(target_file)
            else:
                # 如果不允许覆盖，就抛出异常
                raise Exception('目标目录该文件已经存在，无法复制！')

        shutil.copy2(file, target_file)



    """集合化查询结果"""

    def queryToDict(self, models):
        if models is None:
            return []
        if (isinstance(models, list)):
            if (len(models) == 0):
                return []
            elif (isinstance(models[0], Model)):
                lst = []
                for model in models:
                    gen = self.__model_to_dict(model)
                    dit = dict((g[0], g[1]) for g in gen)
                    lst.append(dit)
                return lst
            else:
                res = self.__result_to_dict(models)
                return res
        else:
            if (isinstance(models, Model)):
                gen = self.__model_to_dict(models)
                dit = dict((g[0], g[1]) for g in gen)
                return dit
            else:
                res = dict(zip(models.keys(), models))
                self.__find_datetime(res)
                return res
    # 当结果为result对象列表时，result有key()方法
    def __result_to_dict(self, results):
        res = [dict(zip(r.keys(), r)) for r in results]
        # 这里r为一个字典，对象传递直接改变字典属性
        for r in res:
            self.__find_datetime(r)
        return res

    def __model_to_dict(self, model):  # 这段来自于参考资源
        for col in model.__table__.columns:
            if isinstance(col.type, DateTime):
                value = self.__convert_datetime(getattr(model, col.name))
            elif isinstance(col.type, Numeric):
                value = float(getattr(model, col.name))
            else:
                value = getattr(model, col.name)
            yield (col.name, value)

    def __find_datetime(self, value):
        for v in value:
            if (isinstance(value[v], cdatetime)):
                value[v] = self.__convert_datetime(value[v])  # 这里原理类似，修改的字典对象，不用返回即可修改

    def __convert_datetime(self, value):
        if value:
            if (isinstance(value, (cdatetime, DateTime))):
                return value.strftime("%Y-%m-%d %H:%M:%S")
            elif (isinstance(value, (cdate, Date))):
                return value.strftime("%Y-%m-%d")
            elif (isinstance(value, (Time, time))):
                return value.strftime("%H:%M:%S")
        else:
            return ""


    
utils = Utils()

