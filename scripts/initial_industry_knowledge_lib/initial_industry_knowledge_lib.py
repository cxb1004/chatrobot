import os
import sys

from common.config import Config
from common.db import *
from common.log import Log
from common.textSimilarity import CosSim
from common.utils import *

basePath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(basePath)
currentFileName = os.path.basename(__file__)

SIM_IDX = 0.6

print('初始化...')
try:
    baseConfig = Config()
    print('配置文件--------ok')
    log = Log()
    print('日志文件--------ok')
    db_user = baseConfig.get_value('db', 'user')
    db_pass = baseConfig.get_value('db', 'password')
    db_host = baseConfig.get_value('db', 'host')
    db_port = baseConfig.get_value('db', 'port')
    db_schema = baseConfig.get_value('db', 'database')
    db_charset = baseConfig.get_value('db', 'charset')
    conn = create_db_connection(user=db_user, password=db_pass, host=db_host, port=db_port, schema=db_schema,
                                charset=db_charset)
    print('数据库连接------ok')
    simUtils = CosSim()
    print('比较器----------ok')
except Exception as e:
    print(str(e))
    print('初始化失败，程序结束')
    exit(999)
print('初始化成功，程序开始运行')


def compareItems(baseItem, item):
    baseQuestion = baseItem.get("question")
    question = item.get("question")
    sim_value = simUtils.getSimilarityIndex(baseQuestion, question)
    if sim_value >= SIM_IDX:
        return True
    return False


def updateGroupData(group):
    global GROUP_NUM
    ids = ""
    for item in group:
        ids = ids + str(item.get("id")) + ","
    if not isNullOrBlank(ids):
        ids = ids[0:ids.__len__() - 1]
    groupString = str(GROUP_NUM)

    sql = '''update cloud_customer_service.rbt_industry_knowledge_lib_init_data set `group` =:groupString where id in ({}) ''' \
        .format(ids)
    params = {'groupString': groupString}
    executeBySQL(conn=conn, sql=sql, params=params)
    log.info("分组[{}]数据{}条，保存成功".format(groupString, group.__len__()))
    GROUP_NUM = GROUP_NUM + 1


def updateIndustryStatus(industry_id):
    sql = '''update cloud_customer_service.rbt_industry_knowledge_lib_init_data set status =1 where industry_id=:industry_id '''
    params = {'industry_id': industry_id}
    executeBySQL(conn=conn, sql=sql, params=params)


log.info("程序开始...")

sql = '''select distinct(industry_id) industry_id from cloud_customer_service.rbt_industry_knowledge_lib_init_data where status=0 order by industry_id asc'''
industry_ids = queryBySQL(conn=conn, sql=sql)
log.info("一共有{}个行业需要分析".format(industry_ids.__len__()))

for industry_data in industry_ids:

    GROUP_NUM = 1
    try:
        industry_id = industry_data.get('industry_id')
        log.info("开始处理行业：{}".format(industry_id))

        sql = '''select id, question from cloud_customer_service.rbt_industry_knowledge_lib_init_data where industry_id=:industry_id order by id asc'''
        params = {'industry_id': industry_id}
        queryData = queryBySQL(conn=conn, sql=sql, params=params)
        id_sentence_array = []
        for data in queryData:
            id_sentence_array.append({"id": data.get("id"), "question": data.get("question")})

        while id_sentence_array.__len__() > 1:
            group = []
            baseItem = id_sentence_array[0]
            group.append(baseItem)

            for item in id_sentence_array[1:]:
                if compareItems(baseItem, item):
                    group.append(item)
            updateGroupData(group)
            id_sentence_array = [item for item in id_sentence_array if item not in group]
            log.info("剩余数据量：{}".format(id_sentence_array.__len__()))

        if id_sentence_array.__len__() == 1:
            group = []
            group.append(id_sentence_array[0])
            updateGroupData(group)

        updateIndustryStatus(industry_id)

        log.info("分组数量：{}".format(GROUP_NUM))
        log.info("行业处理完毕：{}".format(industry_id))
    except Exception as e:
        log.error_ex("行业处理出错：{}".format(industry_id))

log.info("程序完成...")
