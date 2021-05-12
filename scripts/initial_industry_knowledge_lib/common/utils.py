import datetime
import time
import uuid


# from datetime import datetime


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


def calculatePageParameters(all_records, per_page, current_page):
    """
    计算翻页的参数
    :param all_records: 记录总数
    :param per_page: 每页条数
    :param current_page: 当前页
    :return:
    """
    start = 0
    offset = 0
    max_page = 1
    if all_records == 0 or per_page == 0 or current_page < 1:
        return start, offset, max_page

    rest = all_records % per_page
    page = all_records // per_page
    if rest == 0:
        # 如果可以整除，那么
        max_page = page
    else:
        max_page = page + 1

    if current_page < 1:
        current_page = 1
    if current_page > max_page:
        current_page = max_page
    start = (current_page - 1) * per_page

    # 计算偏移量
    if rest > 0 and current_page == max_page:
        offset = rest
    else:
        offset = per_page

    return max_page, start, offset


def getRobotUnloadTime(period=None):
    """
    生成机器人的自动卸载时间
    :param period:秒数
    :return:
    """
    if period is None:
        unload_time = datetime.datetime.now()
    else:
        unload_time = datetime.datetime.now() + datetime.timedelta(seconds=period)
    return unload_time


def timeCompareWithNow(t):
    """
    比较当前时间和卸载时间，如果结果是小于1，就卸载
    :param t:
    :return:
    """
    current_time = datetime.datetime.now()
    rtn = timeCompare(current_time, t)
    return rtn


def timeCompare(time1, time2):
    """
    比较两个时间， time1<time2 1
    :param time1:
    :param time2:
    :return:
    """
    f1 = time1.time()
    f2 = time2.time()
    if f1 == f2:
        return 0
    elif f1 > f2:
        return -1
    elif f1 < f2:
        return 1


def clearCorpusData(data):
    """
    文本数据在转化成json的时候，需要对特殊字符进行一些处理
    :param data:
    :return:
    """
    # 去除回车、换行、制表符
    data.replace("\n", "") \
        .replace("\r", "") \
        .replace("\n\r", "") \
        .replace("\r\n", "") \
        .replace("\t", "") \
        .replace("\\\"", "\"") \
        .replace("				", "")

    # 破坏格式的字符转成中文的
    data.replace('":"{"', "”：“『”") \
        .replace('":"', '“：”') \
        .replace('","', "“，”") \
        .replace('":{"', "“：『”") \
        .replace('"},"', "“』，”") \
        .replace(',"', "，”") \
        .replace('{"', "『“") \
        .replace('"}', "”』") \
        .replace('":', "“：") \
        .replace('"', '”')
    return data

# time1 = datetime.datetime.now()
# time.sleep(2)
# time2 = datetime.datetime.now()
# print(timeCompare(time1,time2))
