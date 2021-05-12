"""
本文件是用于
1、许栋栋根据行业ID（二级行业），从许栋栋处获取该行业下所有企业的行业知识库
把标准问题和答案存储到cloud_customer_service.rbt_industry_knowledge_lib_init_data表
2、使用聚类分析功能，对表里的数据进行分析，
2.1 接受industry_id作为读入参数，检查数据是否存在，不存在就结束
2.2 设置数据的status=0（重复运行）
2.3 开始进行分析，分级结果以id作为分组依据
2.4 分析完成之后，同组的ID取名：分组1，分组2，以此类推
2.5 分组名更新数据表
2.6 行业数据运行完成之后，这个行业下的数据设置status=1（分析完成）
3、分析结果数据会显示到saas管理平台：
【机器人行业库】-【初始行业库】
4、界面上进行【处理】操作：把数据添加到行业库
处理之后，把这个数据的status=2

行业机器人需要返回实体ID（分组、标签都是一个概念）
"""
import os
import sys

from common.config import Config
from common.db import *
from common.log import Log
from common.textSimilarity import CosSim
from common.utils import *

# 当前目录
basePath = os.path.abspath(os.path.dirname(__file__))
# 设置当前目录为执行运行目录
sys.path.append(basePath)
# 获取文件名（含后缀）
currentFileName = os.path.basename(__file__)

SIM_IDX = 0.6

print('初始化...')
try:
    baseConfig = Config()
    print('配置文件--------ok')
    logFile = os.path.join(basePath, currentFileName.replace('.py', '.log'))
    log = Log(logFile)
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
# 1、获得尚未处理的行业ID
sql = '''update rbt_industry_knowledge_lib_init_data set `group`=null, status=0'''
executeBySQL(conn=conn, sql=sql)

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
            # 去掉已经处理过的数据
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
