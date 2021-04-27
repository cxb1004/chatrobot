from flask_module.db_utils import *


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
    # , 'use_model': RobotConstants.KNOWLEDGE_USE_MODEL_NO_PASS
    sql = '''select id, parent_id,question,use_model FROM ai_chatrobot.rbt_knowledge where rbt_id=:rbt_id order by parent_id asc, id asc'''
    params = {'rbt_id': rbt_id}
    queryData = queryBySQL(app=app, sess=sess, sql=sql, params=params)
    # 知识库的结构：  文本：id   id有可能重复，如果文本有重复，后面的数据替换前面的数据
    # full是整个知识库，用于模型判断结果的评分； corpus是使用
    full = {}
    corpus = {}
    for id_pid_q in queryData:
        id = id_pid_q.get('id')
        pid = id_pid_q.get('parent_id')
        q = id_pid_q.get('question')
        use_model = id_pid_q.get('use_model')

        if pid == '0' or pid is None:
            # 如果是标准问题, 则添加<question, id>
            if use_model == 0:
                corpus[q] = id
            full[q] = id
        else:
            # 如果是相似问题, 则添加<question, parent_id>
            if use_model == 0:
                corpus[q] = id
            full[q] = id
    return corpus, full


8
