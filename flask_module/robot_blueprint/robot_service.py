from flask_module.robot_blueprint import robot_blueprint

from flask_module.robot_blueprint.Model.rbt_robot import Robot

ROBOT_LIST = {}


@robot_blueprint.route('/service/answer', methods=['POST'])
def answer():
    """
    机器人回答问题
    :return:
    """
    pass


@robot_blueprint.route('/service/loadRobot', methods=['POST'])
def load_robot():
    """
    根据rbt_id载入机器人
    :return:
    """
    pass


@robot_blueprint.route('/service/listRobots', methods=['POST'])
def list_robots():
    """
    获得所有载入的机器人列表信息
    :return:
    """
    pass


@robot_blueprint.route('/service/getRobotDetail', methods=['POST'])
def get_robot_detail():
    """
    获得某个机器人的详细信息
    :return:
    """
    pass


@robot_blueprint.route('/service/unloadRobot', methods=['POST'])
def unload_robot():
    """
    卸载机器人
    :return:
    """
    pass


@robot_blueprint.route('/service/refreshRobot', methods=['POST'])
def refresh_robot():
    """
    更新机器人
    :return:
    """
    pass
