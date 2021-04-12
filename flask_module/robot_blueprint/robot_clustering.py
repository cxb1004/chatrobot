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

from flask import request,current_app

from flask_module.log_manage import ManageLog as mlog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint


def has_running_cluster_task(rbt_id):
    """
    TODO 检查是否处在运行中的聚类分析任务
    :param rbt_id:
    :return: True:存在运行中的聚类分析任务；False:不存在运行中的聚类分析任务；
    """
    return False


def transferJsonToList(json_data):
    rtn = []
    return rtn


def saveTalkDataToDB(current_app, company_id, rbt_id, original_data):
    pass


@robot_blueprint.route('/manager/startClusterAnalysis', methods=['POST'])
def start_cluster_analysis():
    """
    1、j
    :return:
    """
    mlog.info('接收聚类分析请求...')
    rbt_id = request.form.get('rbt_id', type=str)
    company_id = request.form.get('company_id', type=str)
    if rbt_id is None:
        return_fail('缺少参数：{}'.format('rbt_id'))

    # 1、检查是否存在运行中的聚类分析任务
    hasRunningTask = has_running_cluster_task(rbt_id)
    if hasRunningTask:
        return return_fail('机器人【{}】存在运行中的聚类分析任务，请耐心等待当前任务执行完毕'.format(rbt_id))

    # 2、从post请求中获得json，解析之后存入rbt_datamining_data表
    #
    talk_data = request.form.get('talk_data', type=str)
    # 把字符串转化为Json对象
    json_data = json.load(talk_data)
    # 把json对象转化为List数据结构（为了尽快结束请求，这里不做数据清洗，把原始数据存入数据表）
    original_data = transferJsonToList(json_data)
    # 把聊天数据存入到数据库，完成数据存储（容错处理，遇到错误在日志中报错，不抛出异常）
    saveTalkDataToDB(current_app, company_id, rbt_id, original_data)

    #  创建定时任务
    createNewClusterAnalysisTask(company_id,rbt_id)

    mlog.info('完成聚类分析请求')
    return jsonResultVo(CODE_SUCCES, '请求已经接收，正在启动聚类分析任务，请耐心等待运行结束', '')
