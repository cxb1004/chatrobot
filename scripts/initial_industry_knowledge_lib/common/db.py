import sqlalchemy
from sqlalchemy import DateTime, Date, Time, text
from datetime import datetime as cdatetime


def create_db_connection(user=None, password=None, host=None, port=None, schema=None, charset=None):
    conn = None
    try:
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (user, password, host, port, schema, charset),
            max_overflow=10,
            echo=True
        )
        conn = engine.connect()
    except Exception as e:
        raise e
    finally:
        return conn


def queryBySQL(conn=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param conn:使用app的默认数据库连接进行查询
    :param sess:使用session来控制事务
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return:
    """
    if sess is None:
        statement = text(sql)
        db_result = conn.execute(statement, params)
        data = dbResultToDict(list(db_result))
    else:
        statement = text(sql)
        db_result = sess.execute(statement, params)
        data = dbResultToDict(list(db_result))
    return data


def executeBySQL(conn=None, sess=None, sql=None, params=None):
    """
    用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
    :param app:使用app的默认数据库连接进行查询
    :param sess:使用session来控制事务
    :param sql:原生SQL
    :param params: SQL使用的参数
    :return: 影响条数
    """
    if sess is None:
        statement = text(sql)
        resultProxy = conn.execute(statement, params)
    else:
        statement = text(sql)
        resultProxy = sess.execute(statement, params)
    return resultProxy.rowcount


# def countBySQL(conn=None, sess=None, sql=None, params=None):
#     """
#     用原生SQL进行查询，查询完成以后，把结果集转化为字典列表，字典的key就是字段名
#     :param app:使用app的默认数据库连接进行查询
#     :param sess:数据库连接
#     :param sql:原生SQL
#     :param params: SQL使用的参数
#     :return:
#     """
#     if sess is None:
#         conn = db.get_engine(app)
#         statement = text(sql)
#         db_result = conn.execute(statement, params)
#         data = dbResultToDict(list(db_result))
#     else:
#         statement = text(sql)
#         db_result = sess.execute(statement, params)
#         data = dbResultToDict(list(db_result))
#
#     return int(data[0].get('count'))


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
