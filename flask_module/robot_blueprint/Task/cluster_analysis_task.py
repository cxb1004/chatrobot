import json

from flask import current_app

from flask_module.corpus_utils import *
from flask_module.db_utils import *
from flask_module.log_cluster import ClusterLog
from flask_module.robot_blueprint.Model.rbt_knowledge import getKnowledgeDataForClusterAnalysis
from flask_module.robot_blueprint.Model.rbt_task import RobotTask
from flask_module.textSimilarity import CosSim
from flask_module.utils import *

clog = ClusterLog()

# 相似度比较的阀值
DEFALUT_SIM_IDX = 0.8
# 分组的最小数量,不包括和知识库相似的
DEFALUT_GROUP_NUM = 3


def getTaskIDString(_robot_list):
    """
    获得task_id列表，用于sql操作
    :param _robot_list:
    :return:
    """
    task_id_str = ''
    for robot in _robot_list:
        id = robot.get('task_id')
        task_id_str = task_id_str + "'" + id + "',"
    if task_id_str != '':
        task_id_str = task_id_str[:task_id_str.__len__() - 1]
    return task_id_str


def saveClusterResult(task_id=None, rbt_id=None, qid=None, group=None):
    """
    存储一个分组的聚类分析结果
    :param task_id:
    :param rbt_id:
    :param qid:
    :param group:
    :return:
    """
    sql = '''INSERT INTO ai_chatrobot.rbt_datamining_result(task_id,rbt_id,knowledge_id,questions,created_at) VALUES(:task_id,:rbt_id,:knowledge_id,:questions,now())'''
    params = {'task_id': task_id, 'rbt_id': rbt_id, 'knowledge_id': qid, 'questions': str(group)}
    executeBySQL(app=current_app, sql=sql, params=params)
    clog.debug("标准问题[{}]下的分析结果数据保存成功".format(qid))


def cluster_by_task(task_id, rbt_id, params):
    """
    3.1 获得这个机器人的知识库knowledge_lib
    3.2 获得需要分析的预料数据corpus(合并多个任务的corpus)
    3.3 删除这个任务下已有的分析数据
    3.4 先结合知识库进行相似度比较，符合相似度阀值的，记录：
    question_id:标准问题ID
    questions: [txt1,txt2...]
    记录之后，text文本从corpus移除
    所有知识库里的语句比较完之后，存入一次数据库  （保存之前先删除数据，这样可以重复运行）
    3.5 剩余的corpus里的数据依次进行两两比较
    3.5.1 取第一条数据，后面的数据和它比较，满足阀值的成组
    3.5.2 如果组的数量满足阀值，就存入数据库，并从corpus里面移除相关数据
    3.5.3 如果组的数量不满足阀值，移除第一条数据，开始下一个循环
    :param task_id:
    :param rbt_id:
    :param params:
    :return:
    """
    # 获得聚类分析使用的参数
    clog.info("设置聚类分析任务的参数...")
    try:
        params_json = json.loads(params)
        sim_idx = params_json.get('sim_idx')
        group_num = params_json.get('group_num')
        if isNullOrBlank(sim_idx):
            sim_idx = DEFALUT_SIM_IDX
        if isNullOrBlank(group_num):
            group_num = DEFALUT_GROUP_NUM
    except Exception as ex:
        clog.warn("聚类分析参数解析出错，采用默认参数！")
        sim_idx = DEFALUT_SIM_IDX
        group_num = DEFALUT_GROUP_NUM
    clog.info("聚类分析任务的参数设置完毕：sim_idx：{}   group_num：{}".format(sim_idx, group_num))

    # 3.1 获得这个机器人的知识库knowledge_lib
    knowledge_lib = getKnowledgeDataForClusterAnalysis(app=current_app, rbt_id=rbt_id)
    # 获得问题文本
    knowledges = knowledge_lib.keys()
    clog.info("获取机器人[{}]的知识库数据{}条".format(rbt_id, knowledges.__len__()))

    # 3.2 获得需要分析的预料数据corpus(合并多个任务的corpus)
    sql = '''select content from rbt_datamining_data where task_id in (select task_id from rbt_task where type=:type and status=:status and rbt_id=:rbt_id) '''
    params = {'type': RobotTask.TYPE_CLUSTER_ANALYSIS.get('type'),
              'status': RobotTask.STATUS_IN_PROCESS, 'rbt_id': rbt_id}
    queryData = queryBySQL(app=current_app, sql=sql, params=params)
    corpus = []
    for data in queryData:
        c = data.get('content')
        # 对数据进行清晰，去除html标签、去除表情符号、去除特殊字符
        c = removeHtmlTag(removeEmoj(removeTagContent(c, ['img', 'url'])))
        if not isNullOrBlank(c):
            corpus.append(c)
    # 去重
    corpus = list(dict.fromkeys(corpus))
    clog.info("去重之后，待分析的数据有{}条".format(corpus.__len__()))

    # 3.3 删除这个任务下已有的分析数据
    sql = '''delete from rbt_datamining_result where task_id=:task_id'''
    params = {'task_id': task_id}
    delCount = executeBySQL(app=current_app, sql=sql, params=params)
    if delCount > 0:
        clog.info("数据清理完成, 共清理了{}条数据".format(delCount))

    simUtil = CosSim()

    if knowledges.__len__() > 0:
        # 3.4 结合知识库进行相似度比较，符合相似度阀值的，记录：
        # question_id: 标准问题ID
        # questions: [txt1, txt2...]
        # 记录之后，text文本从corpus移除
        # 所有知识库里的语句比较完之后，存入一次数据库  （保存之前先删除数据，这样可以重复运行）
        clog.info("开始结合知识库进行聚类分析...")
        qid_sentences = {}
        # 循环语料库
        for sentence in corpus:
            clog.debug('文本：{}'.format(sentence))
            # 记录这句话和知识库里的哪一句最相似
            max_qid = None
            max_value = 0.0
            # 循环知识库
            for knowledge in knowledges:
                simValue = simUtil.getSimilarityIndex(knowledge, sentence)

                if simValue >= sim_idx and simValue >= max_value:
                    # 根据知识获得知识ID
                    max_qid = knowledge_lib.get(knowledge)
                    max_value = simValue
                    clog.debug("更新最相似值{}  最相似度知识是：{} ".format(simValue, knowledge))

            # 完成对知识库的扫描之后，max_qid就是最贴近的知识，max_value就是最贴近的相似度
            if max_qid is None:
                # 如果这句话和知识库里的数据，没有一个是达到相似指标的，就跳过：
                continue
            else:
                if qid_sentences.get(max_qid) is None:
                    # 如果还没有这个问题ID，就新增一个{qid:[句1]}
                    qid_sentences[max_qid] = [sentence]
                else:
                    # 如果已经有这个问题ID，就追加一个{qid:[句1,句2]}
                    qid_sentences[max_qid].append(sentence)

        # 筛选出分组数量超过阀值的组
        for qid in qid_sentences.keys():
            group = qid_sentences.get(qid)
            if group.__len__() >= group_num:
                # 保存分析结果到结果表
                saveClusterResult(task_id, rbt_id, qid, group)
                # 从待分析数据中，移除已分析的数据，保留未分组或分组数量不足的数据
                corpus = [item for item in corpus if item not in group]
                clog.info("移除已分析的数据，剩余{}条数据待分析...".format(corpus.__len__()))
        clog.info("结合知识库的聚类分析完成")

    # 3.5 剩余的corpus里的数据依次进行两两比较
    clog.info("开始进行两两聚类分析，分析数量为{}条".format(corpus.__len__()))
    group_sentences = []
    # 如果待分析数据数量，不足以分成一组，结束分析
    while corpus.__len__() >= group_num:
        # 重置数组，并且从语料库的第一个句子作为第一个元素
        group_sentences = [corpus[0]]
        clog.debug("剩余语料库数量{}".format(corpus.__len__()))
        clog.debug(group_sentences)
        # 从第二条记录开始做比较
        for item in corpus[1:]:
            simValue = simUtil.getSimilarityIndex(group_sentences[0], item)
            if simValue >= sim_idx:
                group_sentences.append(item)
                clog.debug(group_sentences)
        # 如果分组数量满足阀值，保存数据，并从语料库里面移除这部分数据
        if group_sentences.__len__() >= group_num:
            saveClusterResult(task_id, rbt_id, qid=None, group=group_sentences)

        # 从待分析数据中，移除已分析的数据，保留未分组或分组数量不足的数据
        corpus = [item for item in corpus if item not in group_sentences]
    clog.info("两两聚类分析完成")


def cluster_analysis_task():
    """
    执行聚类分析任务
    为了以后重构分服考虑，单独做成一个py文件
    1、从rbt_task里面获得所有未开始运行的聚类分析任务，以task_id为单位，合并同一个机器人，多条未运行的数据
    2、把所有未运行的数据，设置为运行中
    3、循环每一个task_id，执行如下
    3.1 获得这个机器人的知识库knowledge_lib
    3.2 获得需要分析的预料数据corpus
    3.3 删除这个任务下已有的分析数据
    3.4 先结合知识库进行相似度比较，符合相似度阀值的，记录：
    question_id:标准问题ID
    questions: [txt1,txt2...]
    记录之后，text文本从corpus移除
    所有知识库里的语句比较完之后，存入一次数据库  （保存之前先删除数据，这样可以重复运行）
    3.5 剩余的corpus里的数据依次进行两两比较
    3.5.1 取第一条数据，后面的数据和它比较，满足阀值的成组
    3.5.2 如果组的数量满足阀值，就存入数据库，并从corpus里面移除相关数据
    3.5.3 如果组的数量不满足阀值，移除第一条数据，开始下一个循环
    4、全部分析完成之后，把这个机器人下单所有任务状态置为完成（注意，这么操作可以操作多个任务）
    注意：
    1、由于任务开始的时候，对任务结果数据会先清空，因此可以在有结果数据的时候，随时提交commit，减少内存压力
    2、根据设计，出错的话就进入下一个循环，无需事务控制
    :return:
    """
    clog.info("聚类分析定时任务开始...")

    # 1、从rbt_task里面获得所有未开始运行的聚类分析任务，以task_id为单位
    # 不已机器人为分析单位的原因在于，王宁宁需要根据task_id来查询任务执行情况，并由此查询结果数据
    # 如果以机器人为单位，数据查询和后期清理数据都会有问题
    sql = '''SELECT task_id, company_id, rbt_id, params FROM ai_chatrobot.rbt_task where type=:type and status=:status order by created_at asc'''
    params = {'type': RobotTask.TYPE_CLUSTER_ANALYSIS.get('type'), 'status': RobotTask.STATUS_INIT}
    task_list = queryBySQL(app=current_app, sql=sql, params=params)

    if task_list.__len__() == 0:
        clog.info("没有聚类分析任务需要执行，定时任务结束。")
    else:
        clog.info("一共有{}个聚类分析任务".format(task_list.__len__()))

        # 2、把所有未运行的数据，设置为运行中
        task_ids = getTaskIDString(task_list)
        sql = '''update ai_chatrobot.rbt_task set status=:status1 where task_id in ({}) and status=:status2 and type=:type'''.format(
            task_ids)
        params = {'status1': RobotTask.STATUS_IN_PROCESS, 'status2': RobotTask.STATUS_INIT,
                  'type': RobotTask.TYPE_CLUSTER_ANALYSIS.get('type'), 'rbt_id': task_ids}
        updateCount = executeBySQL(app=current_app, sql=sql, params=params)
        clog.info("锁定{}个聚类分析任务".format(updateCount))

        for task in task_list:
            # 3、循环每一个robotID
            try:
                company_id = task.get("company_id")
                task_id = task.get("task_id")
                rbt_id = task.get("rbt_id")
                params = task.get("params")
                clog.info("聚类分析任务{}执行中: companyID={}  rbtID={}".format(task_id, company_id, rbt_id))

                # cluster_by_task(task_id, rbt_id, params)

                clog.info("聚类分析任务{}执行完毕: companyID={}  rbtID={}".format(task_id, company_id, rbt_id))

                sql = '''update ai_chatrobot.rbt_task set status=:status1 where task_id=:task_id'''
                params = {'status1': RobotTask.STATUS_FINISH, 'task_id': task_id}
                updateCount = executeBySQL(app=current_app, sql=sql, params=params)
                if updateCount > 0:
                    clog.info("机器人[{}]的{}个聚类分析任务解锁并设置为结束状态".format(rbt_id, updateCount))
                else:
                    clog.error("机器人[{}]的聚类分析任务解锁失败！".format(rbt_id))
            except Exception as ex:
                clog.error_ex("机器人[{}]聚类任务执行出错！".format(rbt_id))
                # 继续下个机器人
                continue

    clog.info("聚类分析定时任务完成")

