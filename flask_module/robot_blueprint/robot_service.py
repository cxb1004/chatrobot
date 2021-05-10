from flask import request, current_app

from flask_module.db_utils import *
from flask_module.log_service import ServiceLog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint
from flask_module.robot_blueprint.Model.rbt_robot import Robot
from flask_module.robot_blueprint.Model.rbt_task import RobotTask
from flask_module.textSimilarity import CosSim
from flask_module.utils import *

ROBOT_LIST = {}

slog = ServiceLog()

simUtil = CosSim()


def load_robot(rbt_id):
    """
    加载机器人操作：
    1、检查机器人是否已经存在于ROBOT_LIST，如果已经存在，结束函数
    2、获得机器人的基本信息：
    - 机器人ID （传入）
    - 相似度阀值，读取这个机器人配置，如果没有就读取配置文件的基础配置
    - 知识库，允许为空
    - 行业机器人ID：根据机器人所属行业来查询
    - 模型：用于模型判断
    - 机器人自动卸载时间
    3、组件机器人实例，并以rbt_id为主键，放入ROBOT_LIST字典
    4、如果行业机器人ID不为空，就载入行业机器人
    如果出错就报警，但是不影响当前机器人的载入

    :param rbt_id:
    :return:
    """
    global ROBOT_LIST
    # 1、检查机器人是否已经存在于ROBOT_LIST，如果已经存在，结束函数
    if rbt_id in ROBOT_LIST.keys():
        slog.warn("机器人已经加载，无需操作！")

    # 2、获得机器人的基本信息,组件机器人实例
    cRobot = Robot()
    try:
        cRobot.assemble(rbt_id=rbt_id)
    except Exception as ex:
        slog.error(str(ex))
        errMsg = "加载机器人{}失败，请联系系统管理员！".format(rbt_id)
        raise Exception(errMsg)

    # 3、rbt_id为主键，放入ROBOT_LIST字典
    ROBOT_LIST[rbt_id] = cRobot
    slog.info("企业机器人{}载入成功".format(rbt_id))

    # 4、如果行业机器人ID不为空，就载入行业机器人
    industry_robot_id = cRobot.getIndustryRobotID()
    if industry_robot_id is not None and industry_robot_id not in ROBOT_LIST.keys():
        industry_robot = Robot()
        industry_robot.assemble(industry_robot_id)
        ROBOT_LIST = {industry_robot_id, industry_robot}


def load_industry_robot(industry_robot_id):
    # TODO 由于暂时没有行业机器人
    pass


def mergeAnswer(c_answers, i_answers):
    """
    合并行业模型和企业模型的判断
    返回的数据可以根据业务随时进行调整
    目前的合并逻辑如下：
    1、把企业机器人答案/行业机器人答案进行合并
    2、按照答案的simValue进行降序排列
    3、获得排序前五大条目，组成最终列表数据，进行返回
    :param c_answers:
    :param i_answers:
    :return:
    """
    if i_answers is not None:
        c_answers.extend(i_answers)
    c_answers.sort(key=lambda i: i['sim_value'], reverse=True)

    # TODO 这里的5是最终返回给前端的数据，重构的时候写到配置文件里
    if c_answers.__len__() > 5:
        cnt = 5
    else:
        cnt = c_answers.__len__()
    return c_answers[:cnt]


@robot_blueprint.route('/service/getAnswerText', methods=['POST'])
def getAnswerText():
    """
    测试用，把answer也查询出来返回给前端
    :param rtn_answer:
    :return:
    """
    rbt_id = request.form.get('rbt_id', type=str)
    question_id = request.form.get('question_id', type=str)
    sql = '''select answer FROM ai_chatrobot.rbt_knowledge where id=:question_id and rbt_id=:rbt_id'''
    params = {'rbt_id': rbt_id, 'question_id': question_id}
    queryData = queryBySQL(app=current_app, sql=sql, params=params)
    if queryData.__len__() > 0:
        return return_success(queryData[0]["answer"])
    else:
        return return_success("回答不出")


@robot_blueprint.route('/service/answer', methods=['POST'])
def inf_answer():
    """
        机器人回答问题
        1、接收参数,如果参数缺失，就返回错误
        - rbt_id 机器人ID
        - question 访客的问题
        2、根据rbt_id，在列表中确认机器人是否存在
        2.1 如果不存在，就load机器人实例
        2.1.1 load成功，就把机器人实例加到ROBOT_LIST里面，用rbt_id作为主键
        2.1.2 load失败，返回异常信息
        3、从ROBOT_LIST里面提取企业机器人实例cRobot
        4、使用企业机器人实例cRobot进行answer回答，分别获得前n个知识库匹配的数据，以及模型判断的结果
        5、获得企业机器人cRobot的所属行业机器人ID
        通过企业机器人所属行业，查询是否存在行业机器人（这个逻辑在创建企业机器人的时候做）
        5.1 如果企业机器人cRobot没有配置行业，跳过
        5.2 如果企业机器人cRobot所属行业（有行业ID），还没有配置行业机器人，跳过
        5.3 如果企业机器人cRobot所属行业有行业机器人，就获取ID
        6、根据行业机器人ID，在ROBOT_LIST里面查询是否已加载行业机器人
        6.1 如果已经加载，直接获得行业机器人实例iRobot
        6.2 如果尚未加载，根据行业机器人ID进行加载
        如果加载过程出错，发出警告，跳过 （不影响返回企业机器人答案）
        7、使用行业机器人iRobot进行回答
        8、根据question_id,整合两部分的答案，返回数据
        - question_id:
        - idx_value:
        - type: k/m   k代表知识库，m代表模型判断
        - tag：i/c    i代表行业机器人/通用机器人   c代表企业机器人
        9、在调用answer接口之后，更新机器人的卸载时间(包括行业机器人和企业机器人)
    :return:
        - question_id:
        - idx_value:
        - type: k/m   k代表知识库，m代表模型判断
        - tag：i/c    i代表行业机器人/通用机器人   c代表企业机器人
    """
    # 1、接收参数, 如果参数缺失，就返回错误
    rbt_id = request.form.get('rbt_id', type=str)
    question = request.form.get("question", type=str)
    if isNullOrBlank(rbt_id) or isNullOrBlank(question):
        return return_fail("参数缺失！")

    # 2、根据rbt_id，在列表中确认机器人是否存在
    if rbt_id not in ROBOT_LIST.keys():
        try:
            # 载入机器人
            load_robot(rbt_id)
        except Exception as ex:
            errMsg = "企业机器人{}载入失败，请联系系统管理员！".format(rbt_id)
            slog.error_ex(errMsg)
            return return_fail(errMsg)
    # 3、从ROBOT_LIST里面提取企业机器人实例cRobot
    cRobot = ROBOT_LIST.get(rbt_id)
    if cRobot is None:
        errMsg = "企业机器人{}调用失败，请联系系统管理员！".format(rbt_id)
        return return_fail(errMsg)

    # 4、使用企业机器人实例cRobot进行answer回答，分别获得前n个知识库匹配的数据，以及模型判断的结果】、
    try:
        c_answers = cRobot.answer(simUtil, question)
    except Exception as ex:
        slog.error_ex("机器人回答出错！")
        c_answers = None

    # 5、获得企业机器人cRobot的所属行业机器人ID
    industry_robot_id = cRobot.getIndustryRobotID()
    # 6、根据行业机器人ID，在ROBOT_LIST里面查询是否已加载行业机器人
    if industry_robot_id is not None:
        # 6.2 如果尚未加载，根据行业机器人ID进行加载
        if industry_robot_id not in ROBOT_LIST.keys():
            try:
                load_industry_robot(industry_robot_id)
            except Exception as ex:
                # 如果加载过程出错，发出警告，跳过 （不影响返回企业机器人答案）
                warnMsg = "企业机器人{}载入失败，请联系系统管理员！".format(rbt_id)
                slog.warn(warnMsg)

        # 6.1 如果已经加载，直接获得行业机器人实例iRobot
        iRobot = ROBOT_LIST.get(industry_robot_id)
        if iRobot is None:
            # 如果加载过程出错，发出警告，跳过 （不影响返回企业机器人答案）
            slog.warn("行业机器人调用失败，请联系管理员！".format(industry_robot_id))
    else:
        # 如果企业机器人本身没有行业机器人配置（企业机器人没有行业 / 有行业但是没有生成行业机器人）
        # 设置行业机器人为空，不影响回答操作
        iRobot = None

    # 7、使用行业机器人iRobot进行回答
    i_answers = None
    if iRobot is not None:
        i_answers = iRobot.answer(question)

    # 根据question_id,整合两部分的答案，返回数据
    rtn_answer = mergeAnswer(c_answers, i_answers)
    slog.debug("问题：{}  \n 答案为：{}".format(question, rtn_answer))
    return return_success(rtn_answer)


@robot_blueprint.route('/service/loadRobot', methods=['POST'])
def load_robot_manually():
    """
    手动载入机器人
    :return:
    """
    rbt_id = request.form.get('rbt_id', type=str)
    if isNullOrBlank(rbt_id):
        return return_fail("机器人ID缺失！")

    try:
        slog.info("开始载入机器人:{}...".format(rbt_id))
        load_robot(rbt_id)
        slog.info("机器人:{}载入完成".format(rbt_id))
    except Exception as ex:
        errMsg = "机器人{}载入失败".format(rbt_id)
        slog.error_ex(errMsg)
        return return_fail(errMsg)


@robot_blueprint.route('/service/unloadRobot', methods=['POST'])
def unload_robot_manualy():
    """
    人工卸载机器人
    :return:
    """
    rbt_id = request.form.get('rbt_id', type=str)
    if isNullOrBlank(rbt_id):
        return return_fail("机器人ID缺失！")

    # 如果机器人已经存在，就从列表中卸载该
    if rbt_id in ROBOT_LIST.keys():
        ROBOT_LIST.pop(rbt_id)
    else:
        return return_fail("机器人[{}]不存在列表中！".format(rbt_id))


def updateKnowledgeByRobot(rbt_id):
    robot = ROBOT_LIST.get(rbt_id)
    if robot is None:
        slog.info("机器人实例不在线，无需更新知识库")
    else:
        robot.updateKnowledge(rbt_id)
        ROBOT_LIST[rbt_id] = robot
        slog.info("机器人知识库更新成功：{}".format(rbt_id))


@robot_blueprint.route('/service/knowledgeUpdateTask', methods=['POST'])
def knowledge_update_task():
    """
    更新机器人知识库
    目前只做知识库的更新，模型的更新放在另外一个模块里面
    1、查询rbt_task是否有需要更新知识库的机器人数据，有就获取任务，并设置任务状态为1
    2、查询当前机器人服务中，是否有这个机器人，如果没有就跳过
    （机器人启动的时候，会自动载入最新的知识库，所以无需在这里做）
    3、如果有，就读取这个机器人的实例，并更新其中知识库的数据
    4、执行完成之后，把这个任务状态设置为100
    :return:
    """
    slog.info("开始更新机器人知识库...")
    # 1、查询rbt_task是否有需要更新知识库的机器人数据，有就获取任务，并设置任务状态为1
    sql = '''select task_id,rbt_id,params from rbt_task where status=:status and type=:type order by created_at asc'''
    params = {'status': RobotTask.STATUS_INIT, 'type': RobotTask.TYPE_SYNC_KNOWLEDGE.get('type')}
    queryData = queryBySQL(app=current_app, sql=sql, params=params)

    if queryData.__len__() == 0:
        slog.info("没有更新知识库的任务，无需更新机器人")
    else:
        # 获得需要操作的任务列表
        taskIDs_in_str = ''
        for data in queryData:
            taskIDs_in_str = taskIDs_in_str + "'" + data.get('task_id') + "',"
        taskIDs_in_str = taskIDs_in_str[0:taskIDs_in_str.__len__() - 1]

        # 锁定当前任务
        sql = '''update rbt_task set status=:status where task_id in ({}) '''.format(taskIDs_in_str)
        params = {'status': RobotTask.STATUS_IN_PROCESS}
        executeBySQL(app=current_app, sql=sql, params=params)

        for data in queryData:
            task_id = data.get('task_id')
            rbt_id = data.get('rbt_id')
            params = data.get('params')

            try:
                # 完成单个机器人的知识库更新
                updateKnowledgeByRobot(rbt_id)

                # 更新完成之后，任务状态更新
                sql = '''update rbt_task set status=:status where task_id=:task_id'''
                params = {'status': RobotTask.STATUS_FINISH, 'task_id': task_id}
                executeBySQL(app=current_app, sql=sql, params=params)
            except Exception as ex:
                slog.error_ex("机器人更新知识库失败：[rbt_id]")
                # 更新失败之后，任务状态更新
                sql = '''update rbt_task set status=:status where task_id=:task_id'''
                params = {'status': RobotTask.STATUS_FINISH_EX, 'task_id': task_id}
                executeBySQL(app=current_app, sql=sql, params=params)

                continue
        slog.info("机器人知识库更新完毕")
    return return_success("机器人知识库更新完毕")
