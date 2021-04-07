from flask import current_app, request

from flask_module.db_utils import getConnect
from flask_module.log_manage import ManageLog as mlog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint
from flask_module.robot_blueprint.Model.rbt_industry import Industry
from flask_module.robot_blueprint.Model.rbt_robot import Robot
from flask_module.robot_blueprint.constants import RobotConstants
from flask_module.utils import isNullOrBlank, getUUID_1


@robot_blueprint.route('/manager/get_industry_list', methods=['POST'])
def get_industry_list():
    """
    直接获得行业列表（一二级）
    :return:
    """
    sql = 'select id, industry_name, industry_parent from cloud_customer_service.ccs_industry1 AS industry order by industry_parent,id asc'
    try:
        industry_list = queryBySQL(app=current_app, sql=sql)
    except Exception as ex:
        mlog.error_ex("执行sql出错：{}".format(sql))
        return return_fail("执行sql出错")
    return return_success(industry_list)


@robot_blueprint.route('/manager/get_industry_by_company', methods=['POST'])
def get_industry_by_company():
    """
    直接获得行业列表（一二级）
    :return:
    """
    sql = 'select id, industry_name, industry_parent from cloud_customer_service.ccs_industry1 AS industry order by industry_parent,id asc'
    try:
        industry_list = queryBySQL(app=current_app, sql=sql)
    except Exception as ex:
        mlog.error_ex("执行sql出错：{}".format(sql))
        return return_fail("执行sql出错")
    return return_success(industry_list)


@robot_blueprint.route('/manager/create_company_robot', methods=['POST'])
def create_company_robot():
    """
    创建企业机器人
    :return:
    """
    # 接收参数
    company_id = request.form.get('company_id', type=int)
    company_name = request.form.get('company_name', type=str)
    industry_name = request.form.get('industry_name', type=str)
    expired_date = request.form.get('expired_date', type=str)

    # 验证参数
    if isNullOrBlank(company_id) or isNullOrBlank(company_name) or isNullOrBlank(industry_name) or isNullOrBlank(
            expired_date):
        return return_fail("参数参数缺失！")

    # 开始执行业务逻辑
    conn = getConnect(current_app)
    try:
        industry = Industry()
        industry_id = industry.getIndustryByName(conn, industry_name)
        if isNullOrBlank(industry_id):
            errMsg = '获取行业ID出错'
            return return_fail(errMsg)
    except Exception as ex:
        errMsg = '获取行业ID出错'
        mlog.error_ex(errMsg)
        return return_fail(errMsg)

    try:
        robot = Robot()
        # uuid_1生成的唯一ID
        robot.rbt_id = getUUID_1()
        # 企业机器人的ID和名字保持一致
        robot.rbt_name = robot.rbt_id
        robot.type = RobotConstants.RBT_TYPE_COMPANY
        robot.company_id = company_id
        robot.company_name = company_name
        robot.industry_id = industry_id
        robot.industry_name = industry_name
        # 默认为启用状态
        robot.status = RobotConstants.RBT_STATUS_ON


    except Exception as ex:
        errMsg = '创建机器人失败！'
        mlog.error_ex(errMsg)
        return return_fail(errMsg)

    return return_success('')
