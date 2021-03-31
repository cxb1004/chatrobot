from flask import current_app
from sqlalchemy import text

from flask_module import db
from flask_module.robot_blueprint import robot_blueprint
from flask_module.db_utils import query
from flask_module.result_json import return_success
from flask_module.db_utils import queryToDict


@robot_blueprint.route('/manager/get_industry_list', methods=['POST'])
def get_industry_list():
    """
    直接获得行业列表（一二级）
    :return:
    """
    test_sql = 'select id, industry_name, industry_parent from cloud_customer_service.ccs_industry AS industry order by industry_parent,id asc'
    data = query(app=current_app, sql=test_sql)
    return return_success(data)