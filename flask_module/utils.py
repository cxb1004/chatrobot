import datetime
import time
import uuid


def strToBool(txt):
    if txt == 'True':
        return True
    elif txt == 'False':
        return False
    elif txt == 'true':
        return True
    elif txt == 'false':
        return False
    elif txt == '0':
        return False
    elif txt == '1':
        return True
    else:
        return None


def getUUID_1():
    """
    生成UUID，36位，例如2ea8df62-9356-11eb-8861-2c6e85a3b49d，是时间戳+服务器Mac地址加密获得
    主要用于机器人ID的生成
    :return: 36位的字符串
    """
    return uuid.uuid1()


def isNullOrBlank(txt):
    """
    判断字符串是否为空值
    :param txt:
    :return:
    """
    if txt is None or str(txt).strip() == '':
        return True
    else:
        return False


def strToDate(txt):
    """
    把字符串转化成Date
    :param txt:
    :return:
    """
    fmt = '%Y-%m-%d'
    time_tuple = time.strptime(txt, fmt)
    year, month, day = time_tuple[:3]
    rtn_date = datetime.date(year, month, day)
    return rtn_date
    print(rtn_date, type(rtn_date))

# txt = '2022-4-13'
# d = strToDate(txt)
# print(d, type(d))
