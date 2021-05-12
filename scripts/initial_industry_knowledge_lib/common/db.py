from datetime import datetime as cdatetime

import sqlalchemy
from sqlalchemy import DateTime, Date, Time, text


def create_db_connection(user=None, password=None, host=None, port=None, schema=None, charset=None):
    conn = None
    try:
        engine = sqlalchemy.create_engine(
            "mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (user, password, host, port, schema, charset),
            max_overflow=10,
            echo=True
        )
        conn = engine.connect()
        return conn
    except Exception as e:
        raise e


def queryBySQL(conn=None, sess=None, sql=None, params=None):
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
    if sess is None:
        statement = text(sql)
        resultProxy = conn.execute(statement, params)
    else:
        statement = text(sql)
        resultProxy = sess.execute(statement, params)
    return resultProxy.rowcount


def dbResultToDict(result=None):
    res = [dict(zip(r.keys(), r)) for r in result]
    for r in res:
        find_datetime(r)
    return res


def find_datetime(value):
    for v in value:
        if isinstance(value[v], cdatetime):
            value[v] = convert_datetime(value[v])


def convert_datetime(value):
    if value:
        if isinstance(value, (cdatetime, DateTime)):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, (cdate, Date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, (Time, time)):
            return value.strftime("%H:%M:%S")
    else:
        return value
