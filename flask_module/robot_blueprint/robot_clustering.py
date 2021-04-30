"""
聚类/分类分析

业务：
1、接受王宁宁传输过来、待分析的数据集，并存储到rbt_datamining_data表
2、在rbt_task里面新建一个数据挖掘任务
3、准备如下数据：
 - 知识库数据（非必须）
 - 相似度（王宁宁传输，可以采用默认配置值，非必须）
 - 待分析数据（王宁宁传输，必须）
4、开始分析数据，并把结果写入rbt_datamining_result里面
具备容错，如果部分数据分析失败，直接跳过
5、随时更新数据挖掘任务的状态，允许王宁宁发起查询状态和挖掘结果
"""
import json

from flask import request, current_app

from flask_module.corpus_utils import *
from flask_module.log_cluster import ClusterLog as clusterLog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint
from flask_module.robot_blueprint.Model.rbt_task import *
from flask_module.robot_blueprint.constants import RobotConstants
from flask_module.utils import *
from flask_module.robot_blueprint.Task.cluster_analysis_task import *


@robot_blueprint.route('/cluster/testTask', methods=['POST'])
def test_schedule_job_task():
    cluster_analysis_task()
    return return_success("调用成功")


def saveDataForCluster(rbt_id, task_id, insert_data):
    # 2、存储数据
    for content in insert_data:
        if content is not None:
            sql = '''INSERT INTO ai_chatrobot.rbt_datamining_data (rbt_id, task_id, content) VALUES (:rbt_id, :task_id, :content)'''
            params = {'rbt_id': rbt_id, 'task_id': task_id, 'content': content}
            try:
                executeBySQL(app=current_app, sql=sql, params=params)
            except Exception as ex:
                clusterLog.error_ex("部分数据插入失败：{} / {} / {}".format(rbt_id, task_id, insert_data))
                continue


def filterDataForClusterAnalysis(company_id, rbt_id, json_data):
    """
    对准备分析的数据进行清理
    1、如果数据已经存在于知识库，去除
    2、去掉IMG标签。URL 标签
    3、去掉手机、邮箱、电话、微信、qq等实体数据
    去除之后如果为空字符串，去除
    这里的验证主要目的是去除无效的记录，降低分析数据的基数
    为了给前端反应，这里不宜做深入的数据清洗。
    :param rbt_id:
    :param company_id:
    :param json_data:
    :return:
    """
    clusterLog.debug("开始对待分析数据进行清洗...")
    clusterLog.debug("过滤前端数据量：{}".format(json_data.__len__()))

    sql = '''select question from rbt_knowledge where company_id=:company_id and rbt_id=:rbt_id'''
    params = {'company_id': company_id, "rbt_id": rbt_id}
    queryData = queryBySQL(app=current_app, sql=sql, params=params)
    knowledge_lib = []
    for item in queryData:
        knowledge_lib.append(item['question'])
    corpus_without_knowledge = list(set(json_data) - set(knowledge_lib))
    clusterLog.debug("对比知识库去重之后的数量：{}".format(corpus_without_knowledge.__len__()))

    filterCorpus = []
    for sentence in corpus_without_knowledge:
        sentence = removeTagContent(sentence, ['img', 'url', 'email', 'phone', 'mobile', 'qq'])
        if not isNullOrBlank(sentence):
            filterCorpus.append(sentence)

    clusterLog.debug("过滤掉一些非分析对象内容，过滤之后的数量{}".format(filterCorpus.__len__()))
    return filterCorpus


@robot_blueprint.route('/cluster/submitClusterRequest', methods=['POST'])
def submit_cluster_request():
    """
    提交聚类分析请求
    1、验证参数
    2、检查机器人是否存在，不存在就报错
    3、检查该机器人是否有聚类分析任务未完成
    如果有，返回错误； 如果没有，继续
    4、数据过滤
    5、数据存储
    6、创建任务
    :return: 任务ID
    """
    clusterLog.info('接收聚类分析请求...')
    rbt_id = request.form.get('rbt_id', type=str)
    company_id = request.form.get('company_id', type=int)
    talk_data = request.form.get('talk_data', type=str)

    # 1、验证参数
    if isNullOrBlank(rbt_id) or isNullOrBlank(company_id) or isNullOrBlank(talk_data):
        return return_fail("参数缺失！")

    # 2、检查机器人是否存在，不存在就报错
    sql = '''SELECT count(rbt_id) count FROM ai_chatrobot.rbt_robot where company_id=:company_id and rbt_id=:rbt_id and status=:status'''
    params = {'company_id': company_id, 'rbt_id': rbt_id, 'status': RobotConstants.RBT_STATUS_ON}
    count = countBySQL(app=current_app, sql=sql, params=params)
    if count == 0:
        return return_fail("机器人不存在：{}".format(rbt_id))
    clusterLog.info("验证机器人存在")

    # 3、检查该机器人是否有聚类分析任务未完成
    sql = '''SELECT count(task_id) count FROM ai_chatrobot.rbt_task where company_id=:company_id and rbt_id=:rbt_id and type=:type and status not in (:state_finish, :status_finish_ex) '''
    params = {'company_id': company_id, 'rbt_id': rbt_id, 'type': RobotTask.TYPE_CLUSTER_ANALYSIS['type'],
              'state_finish': RobotTask.STATUS_FINISH, 'status_finish_ex': RobotTask.STATUS_FINISH_EX}
    count = countBySQL(app=current_app, sql=sql, params=params)
    if count > 0:
        return return_fail("该机器人有聚类分析任务尚未完成，请等待当前任务完成后再提交：{}".format(rbt_id))
    clusterLog.info("没有同类型任务执行，允许提交任务")

    # 4、从post请求中获得json，解析之后存入rbt_datamining_data表
    talk_data = request.form.get('talk_data', type=str)
    try:
        talk_json = json.loads(talk_data)
    except Exception as ex:
        clusterLog.error_ex("解析数据出错！")
        return return_fail("解析数据出错！")

    # 把json对象转化为List数据结构（为了尽快结束请求，这里不做数据清洗，把原始数据存入数据表）
    insert_data = filterDataForClusterAnalysis(company_id, rbt_id, talk_json)

    # 获取task_id
    task_id = getUUID_1()
    #
    # 把聊天数据存入到数据库，完成数据存储（容错处理，遇到错误在日志中报错，不抛出异常）
    saveDataForCluster(rbt_id, task_id, insert_data)

    #  创建定时任务
    createTask(app=current_app, company_id=company_id, rbt_id=rbt_id, task_id=task_id,
               task_type=RobotTask.TYPE_CLUSTER_ANALYSIS)

    clusterLog.info('完成聚类分析请求')
    return return_success(task_id)
