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

from flask_module.db_utils import *
from flask_module.log_cluster import ClusterLog
from flask_module.log_manage import ManageLog as mlog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint
from flask_module.robot_blueprint.Model.rbt_task import *
# from flask_module.db_utils import *
from flask_module.robot_blueprint.constants import RobotConstants
from flask_module.utils import *

clusterLog = ClusterLog()



def filterDataForClusterAnalysis(company_id, rbt_id, json_data):
    """
    对准备分析的数据进行清理
    1、如果数据已经存在于知识库，去除
    2、去掉IMG标签。
    3、去掉快服标签标签
    4、去掉手机、邮箱、电话、微信、qq等实体数据
    去除之后如果为空字符串，去除
    :param rbt_id:
    :param company_id:
    :param json_data:
    :return:
    """
    sql = '''select question from rbt_knowledge where company_id=:company_id and rbt_id=:rbt_id'''
    params = {'company_id':company_id, "rbt_id":rbt_id}


def saveDataForCluster(company_id, rbt_id, insert_data):
    pass


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
    mlog.info('接收聚类分析请求...')
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
    #
    # # 把聊天数据存入到数据库，完成数据存储（容错处理，遇到错误在日志中报错，不抛出异常）
    saveDataForCluster(company_id, rbt_id, insert_data)

    #  创建定时任务

    createTask(app=current_app, company_id=company_id, rbt_id=rbt_id, type=RobotTask.TYPE_CLUSTER_ANALYSIS )

    mlog.info('完成聚类分析请求')
    return jsonResultVo(CODE_SUCCES, '请求已经接收，正在启动聚类分析任务，请耐心等待运行结束', '')




@robot_blueprint.route('/manager/createClusterAnalysisTask', methods=['POST'])
def create_cluster_analysis_task():
    """
    王宁宁这里会把机器人ID,和需要分析的数据传输给我们,存入数据库,并创建任务,通过定时任务去进行分析
    1、接收数据
    1.1 存储数据之前，先检查这个机器人是否已经有分析任务存在，如果存在，就不允许操作
    2、存储数据,
    3、生成任务
    4、返回任务ID
    :return: 返回任务ID,用于随时查阅聚类分析结果
    """
    # 1、接收数据
    rbt_id = request.form.get('rbt_id', type=str)
    company_id = request.form.get('company_id', type=str)
    data = request.form.get('data', type=str)

    if isNullOrBlank(rbt_id) or isNullOrBlank(company_id):
        return return_fail("参数缺失！")

    # 1.1 存储数据之前，先检查这个机器人是否已经有分析任务存在，如果存在，就不允许操作
    isExist = checkUnFinishedTaskExist(app=current_app, rbt_id=rbt_id, task_type=RobotTask.TYPE_CLUSTER_ANALYSIS)
    if isExist:
        return return_fail("当前机器人正在运行一个分析任务，结束以后才可以提交新的任务，请耐心等候！")

    try:
        data_list = json.loads(data)
    except Exception as ex:
        errMsg = '知识库数据转化为json出错！'
        mlog.error_ex(errMsg)
        return return_fail(errMsg)

    # 2、存储数据
    # 先获取uuid作为taskID
    task_id = getUUID_1()
    conn = db.get_engine(current_app)
    Session = sessionmaker(bind=conn)
    session = Session()
    session.begin()
    try:
        # 2、存储数据
        for content in data_list:
            content = clearCorpusData(content)
            if content is not None:
                sql = '''INSERT INTO ai_chatrobot.rbt_datamining_data (rbt_id, task_id, content) VALUES (rbt_id:rbt_id, task_id:task_id, content:content)'''
                params = {'rbt_id': rbt_id, 'task_id': task_id, 'content': content}
                executeBySQL(sess=session, sql=sql, params=params)

        # 3、生成任务
        createTask(sess=session, company_id=company_id, rbt_id=rbt_id, task_type=RobotTask.TYPE_CLUSTER_ANALYSIS)

        session.commit()
    except Exception as ex:
        errMsg = '保存聚类分析数据出错!'
        mlog.error_ex(errMsg)
        session.rollback()
        return return_fail(errMsg)

    # 4、返回任务ID
    return return_success(task_id)
