import time
from datetime import date as cdate
from datetime import datetime as cdatetime

from flask_sqlalchemy import Model
from sqlalchemy import DateTime, Numeric, Date, Time, text

from flask_module import db


def getConnect(app=None):
    """
    开放获得connection对象，用于transaction操作
    :param app:
    :return:
    """
    conn = db.get_engine(app)
    return conn


def getBindConnect(app=None, bind=None):
    """
    开放获得connection对象，用于多数据库
    :param app:
    :return:
    """
    conn = db.get_engine(app, bind)
    return conn


def query(app=None, sql=None, params=None):
    conn = db.get_engine(app)
    statement = text(sql)
    db_result = conn.execute(statement, params)
    data = queryToDict(db_result)
    return data


def query_by_conn(conn=None, sql=None, params=None):
    db_result = conn.execute(sql)
    data = queryToDict(db_result)
    return data


def queryToDict(models):
    """集合化查询结果"""
    res = ''
    if models is None:
        return ""
    if isinstance(models, list):
        if len(models) == 0:
            return ""
        elif isinstance(models[0], Model):
            lst = []
            for model in models:
                gen = model_to_dict(model)
                dit = dict((g[0], g[1]) for g in gen)
                lst.append(dit)
            return lst
        else:
            res = result_to_dict(models)
            return str(res)
    else:
        if isinstance(models, Model):
            gen = model_to_dict(models)
            dit = dict((g[0], g[1]) for g in gen)
            return dit
        else:
            res = dict(zip(models.keys(), models))
            find_datetime(res)
            return str(res)


def find_datetime(value):
    for v in value:
        if isinstance(value[v], cdatetime):
            value[v] = convert_datetime(value[v])  # 这里原理类似，修改的字典对象，不用返回即可修改


def result_to_dict(results):
    # 当结果为result对象列表时，result有key()方法
    res = [dict(zip(r.keys(), r)) for r in results]
    # 这里r为一个字典，对象传递直接改变字典属性
    for r in res:
        find_datetime(r)
    return res


def model_to_dict(model):
    # 这段来自于参考资源
    for col in model.__table__.columns:
        if isinstance(col.type, DateTime):
            value = convert_datetime(getattr(model, col.name))
        elif isinstance(col.type, Numeric):
            value = float(getattr(model, col.name))
        else:
            value = getattr(model, col.name)
        yield (col.name, value)


def convert_datetime(value):
    if value:
        if isinstance(value, (cdatetime, DateTime)):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (cdate, Date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, (Time, time)):
            return value.strftime("%H:%M:%S")
    else:
        return ""

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
