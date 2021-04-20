from flask_module.db_utils import *
from flask_module.robot_blueprint.constants import RobotConstants


def getKnowledgeDataForClusterAnalysis(app=None, sess=None, rbt_id=None):
    """
    获取知识库，用于聚类分析
    :param rbt_id:
    :param sess:
    :param app:
    :return:
    """
    sql = '''select id, parent_id,question FROM ai_chatrobot.rbt_knowledge where rbt_id=:rbt_id order by parent_id asc, id asc'''
    params = {'rbt_id': rbt_id}
    queryData = queryBySQL(app=app, sess=sess, sql=sql, params=params)
    # 知识库的结构：  文本：id   id有可能重复，如果文本有重复，后面的数据替换前面的数据
    knowledge_lib = {}
    for id_pid_q in queryData:
        id = id_pid_q.get('id')
        pid = id_pid_q.get('parent_id')
        q = id_pid_q.get('question')

        if pid == '0' or pid is None:
            # 如果是标准问题, 则添加<question, id>
            knowledge_lib = {q, id}
        else:
            # 如果是相似问题, 则添加<question, parent_id>
            knowledge_lib = {q, pid}
    return knowledge_lib


def getKnowledgeDataForAnswer(app=None, sess=None, rbt_id=None):
    """
    获取知识库，用于线上问答，过滤掉通过模型可以正确判断的语句
    :param rbt_id:
    :param sess:
    :param app:
    :return:
    """
    sql = '''select id, parent_id,question FROM ai_chatrobot.rbt_knowledge where rbt_id=:rbt_id and use_model=:use_model order by parent_id asc, id asc'''
    params = {'rbt_id': rbt_id, 'use_model': RobotConstants.KNOWLEDGE_USE_MODEL_NO_PASS}
    queryData = queryBySQL(app=app, sess=sess, sql=sql, params=params)
    # 知识库的结构：  文本：id   id有可能重复，如果文本有重复，后面的数据替换前面的数据
    knowledge_lib = {}
    for id_pid_q in queryData:
        id = id_pid_q.get('id')
        pid = id_pid_q.get('parent_id')
        q = id_pid_q.get('question')

        if pid == '0' or pid is None:
            # 如果是标准问题, 则添加<question, id>
            knowledge_lib = {q, id}
        else:
            # 如果是相似问题, 则添加<question, parent_id>
            knowledge_lib = {q, pid}
    return knowledge_lib


8
