from flask import current_app

from flask_module.db_utils import *
from flask_module.log_cluster import ClusterLog
# from flask_module.log_manage import ManageLog as mlog
from flask_module.robot_blueprint.Model.rbt_task import RobotTask


def cluster_analysis_task():
    """
    执行聚类分析任务
    为了以后重构分服考虑，单独做成一个py文件
    1、从rbt_task里面获得所有未开始运行的聚类分析任务，以robot_id为单位，合并同一个机器人，多条未运行的数据
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
    clog = ClusterLog()
    clog.info("聚类分析定时任务开始...")

    # conn = db.get_engine(current_app)
    # Session = sessionmaker(bind=conn)
    # session = Session()
    # session.begin()
    # 1、从rbt_task里面获得所有未开始运行的聚类分析任务，以robot_id为单位，合并同一个公司，多条未运行的数据
    sql = '''SELECT company_id, rbt_id, status, params, comment, created_at FROM ai_chatrobot.rbt_task where type=:type and status=:status group by rbt_id  order by created_at asc'''
    params = {'type': RobotTask.TYPE_CLUSTER_ANALYSIS.get('type'), 'status': RobotTask.STATUS_INIT}
    task_list = queryBySQL(app=current_app, sql=sql, params=params)

    if task_list.__len__() == 0:
        clog.info("没有聚类分析任务需要执行，定时任务结束。")
    else:
        clog.info("一共有{}个聚类分析任务需要执行".format(task_list.__len__()))

        # 2、把所有未运行的数据，设置为运行中
        sql = '''update'''

        for task in task_list:
            company_id = task.get("company_id")
            rbt_id = task.get("rbt_id")
            params = task.get("params")
            clog.info("开始执行公司[{}]-机器人[{}]的聚类分析任务".format(company_id,rbt_id))




    clog.info("聚类分析定时任务完成...")
