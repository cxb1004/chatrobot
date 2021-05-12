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
    return uuid.uuid1()


def isNullOrBlank(txt):
    if txt is None or str(txt).strip() == '':
        return True
    else:
        return False


def strToDate(txt):
    fmt = '%Y-%m-%d'
    time_tuple = time.strptime(txt, fmt)
    year, month, day = time_tuple[:3]
    rtn_date = datetime.date(year, month, day)
    return rtn_date
    print(rtn_date, type(rtn_date))


def calculatePageParameters(all_records, per_page, current_page):
    start = 0
    offset = 0
    max_page = 1
    if all_records == 0 or per_page == 0 or current_page < 1:
        return start, offset, max_page

    rest = all_records % per_page
    page = all_records // per_page
    if rest == 0:
        max_page = page
    else:
        max_page = page + 1

    if current_page < 1:
        current_page = 1
    if current_page > max_page:
        current_page = max_page
    start = (current_page - 1) * per_page

    if rest > 0 and current_page == max_page:
        offset = rest
    else:
        offset = per_page

    return max_page, start, offset


def getRobotUnloadTime(period=None):
    if period is None:
        unload_time = datetime.datetime.now()
    else:
        unload_time = datetime.datetime.now() + datetime.timedelta(seconds=period)
    return unload_time


def timeCompareWithNow(t):
    current_time = datetime.datetime.now()
    rtn = timeCompare(current_time, t)
    return rtn


def timeCompare(time1, time2):
    f1 = time1.time()
    f2 = time2.time()
    if f1 == f2:
        return 0
    elif f1 > f2:
        return -1
    elif f1 < f2:
        return 1


def clearCorpusData(data):
    data.replace("\n", "") \
        .replace("\r", "") \
        .replace("\n\r", "") \
        .replace("\r\n", "") \
        .replace("\t", "") \
        .replace("\\\"", "\"") \
        .replace("				", "")

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
