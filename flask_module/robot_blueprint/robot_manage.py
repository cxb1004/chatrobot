from flask import current_app

from flask_module.db_utils import queryBySQL
from flask_module.log_manage import ManageLog as mlog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint


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
