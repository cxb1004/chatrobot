from flask import request

from flask_module.log_service import ServiceLog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint
from flask_module.utils import *

ROBOT_LIST = {}

slog = ServiceLog()


@robot_blueprint.route('/service/answer', methods=['POST'])
def answer():
    """
    机器人回答问题
    1、接收参数,如果参数缺失，就返回错误
    - rbt_id 机器人ID
    - question 访客的问题
    2、根据rbt_id，在列表中确认机器人是否存在
    2.1 如果不存在，就新建机器人实例
    2.1.1 新建成功，就把机器人实例加到ROBOT_LIST里面，用rbt_id作为主键
    2.1.2 新建失败，返回异常信息
    3、从ROBOT_LIST里面提取机器人实例





    2.1 如果存在，就在ROBOT_LIST直接提取机器人对象Robot
    2.2 如果不存在，就尝试加载机器人对象，并放入ROBOT_LIST
    2.2.1 如果加载成功，没有问题
    2.2.2 如果加载失败，返回错误信息
    3、从ROBOT_LIST里面获得ROBOT对象，从中获得行业机器人ID
    3.1 如果没有行业机器人就忽略
    3.2 如果有行业机器人，就加载行业机器人
    3.2.1 如果行业机器人加载成功，就用行业机器人进行问答
    3.2.2 如果行业机器人加载失败，就忽略
    4、使用


    :return:
    """
    rbt_id = request.form.get('rbt_id', type=str)
    question = request.form.get("question",type=str)
    if isNullOrBlank(rbt_id) or isNullOrBlank(question):
        return return_fail("参数缺失！")
    if rbt_id not in ROBOT_LIST.keys():
        pass
    # 从列表中获取机器人
    robot = ROBOT_LIST.get(rbt_id)

    # 如果有行业机器人，那么就要调用行业机器人
    if robot.industry_rbt_id is not None:
        pass


def load_robot(rbt_id):
    """
    1、检查机器人是否已经存在，如果存在，无需导入
    2、获取机器人的运行数据
    - 机器人ID
    - 机器人的语料库（use_model=0）
    - 相似度阀值
    - 机器人的模型
    - 模型判断阀值
    - 行业机器人ID
    - 机器人的自动卸载时间
    :param rbt_id:
    :return:
    """
    if rbt_id in ROBOT_LIST.keys():
        slog.warn("机器人已经加载，无需操作！")

    pass





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


@robot_blueprint.route('/service/updateRobot', methods=['POST'])
def refresh_robot():
    """
    更新机器人
    :return:
    """
    pass
