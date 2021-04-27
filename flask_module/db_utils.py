import time
from datetime import date as cdate
from datetime import datetime as cdatetime

from sqlalchemy import DateTime, Date, Time, text

from flask_module import db


def getBindConnect(app=None, bind=None):
    """
    开放获得connection对象，用于多数据库
    :param app: current_app
    :param bind: 其他DB连接配置名
    :return:
    """
    conn = db.get_engine(app, bind)
    return conn


def queryBySQL(app=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param app:使用app的默认数据库连接进行查询
    :param sess:使用session来控制事务
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return:
    """
    if sess is None:
        conn = db.get_engine(app)
        statement = text(sql)
        db_result = conn.execute(statement, params)
        data = dbResultToDict(list(db_result))
    else:
        statement = text(sql)
        db_result = sess.execute(statement, params)
        data = dbResultToDict(list(db_result))
    return data


def executeBySQL(app=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param app:使用app的默认数据库连接进行查询
    :param sess:使用session来控制事务
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return: 影响条数
    """
    if sess is None:
        conn = db.get_engine(app)
        statement = text(sql)
        resultProxy = conn.execute(statement, params)
    else:
        statement = text(sql)
        resultProxy = sess.execute(statement, params)
    return resultProxy.rowcount


def countBySQL(app=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param app:使用app的默认数据库连接进行查询
    :param sess:数据库连接
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return:
    """
    if sess is None:
        conn = db.get_engine(app)
        statement = text(sql)
        db_result = conn.execute(statement, params)
        data = dbResultToDict(list(db_result))
    else:
        statement = text(sql)
        db_result = sess.execute(statement, params)
        data = dbResultToDict(list(db_result))

    return int(data[0].get('count'))


def dbResultToDict(result=None):
    """
    查询结果集转化为字典类型
    :param result:
    :return:
    """
    # 当结果为result对象列表时，result有key()方法
    res = [dict(zip(r.keys(), r)) for r in result]
    # 这里r为一个字典，对象传递直接改变字典属性
    for r in res:
        find_datetime(r)
    return res


def find_datetime(value):
    """
    把结果里面的日期时间值进行格式化
    :param value:
    :return:
    """
    for v in value:
        if isinstance(value[v], cdatetime):
            # 这里原理类似，修改的字典对象，不用返回即可修改
            value[v] = convert_datetime(value[v])


def convert_datetime(value):
    """
    根据值的类型，分别进行格式化操作
    :param value:
    :return:
    """
    if value:
        if isinstance(value, (cdatetime, DateTime)):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (cdate, Date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, (Time, time)):
            return value.strftime("%H:%M:%S")
    else:
        return value

# 留着备份
# class db_utils(object):
#
#     def queryToDict(self, models):
#         """集合化查询结果"""
#         res = ''
#         if models is None:
#             return ""
#         if (isinstance(models, list)):
#             if (len(models) == 0):
#                 return ""
#             elif (isinstance(models[0], Model)):
#                 lst = []
#                 for model in models:
#                     gen = self.__model_to_dict(model)
#                     dit = dict((g[0], g[1]) for g in gen)
#                     lst.append(dit)
#                 return lst
#             else:
#                 res = self.__result_to_dict(models)
#                 return str(res)
#         else:
#             if (isinstance(models, Model)):
#                 gen = self.__model_to_dict(models)
#                 dit = dict((g[0], g[1]) for g in gen)
#                 return dit
#             else:
#                 res = dict(zip(models.keys(), models))
#                 self.__find_datetime(res)
#                 return str(res)
#
#     def __result_to_dict(self, results):
#         # 当结果为result对象列表时，result有key()方法
#         res = [dict(zip(r.keys(), r)) for r in results]
#         # 这里r为一个字典，对象传递直接改变字典属性
#         for r in res:
#             self.__find_datetime(r)
#         return res
#
#     def __model_to_dict(self, model):
#         # 这段来自于参考资源
#         for col in model.__table__.columns:
#             if isinstance(col.type, DateTime):
#                 value = self.__convert_datetime(getattr(model, col.name))
#             elif isinstance(col.type, Numeric):
#                 value = float(getattr(model, col.name))
#             else:
#                 value = getattr(model, col.name)
#             yield (col.name, value)
#
#     def __find_datetime(self, value):
#         for v in value:
#             if (isinstance(value[v], cdatetime)):
#                 value[v] = self.__convert_datetime(value[v])  # 这里原理类似，修改的字典对象，不用返回即可修改
#
#     def __convert_datetime(self, value):
#         if value:
#             if (isinstance(value, (cdatetime, DateTime))):
#                 return value.strftime("%Y-%m-%d %H:%M:%S")
#             elif (isinstance(value, (cdate, Date))):
#                 return value.strftime("%Y-%m-%d")
#             elif (isinstance(value, (Time, time))):
#                 return value.strftime("%H:%M:%S")
#         else:
#             return ""
