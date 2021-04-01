from flask import current_app
from sqlalchemy import text

from flask_module import db
from flask_module.db_blueprint import db_blueprint
from flask_module.db_utils import queryBySQL,dbResultToDict
from flask_module.result_json import return_success

# log = FlaskLog()


@db_blueprint.route('/test1', methods=['GET', 'POST'])
def test1():
    test_sql = 'SELECT * FROM bigdata.robot_industry WHERE ID=:id'
    data = queryBySQL(app=current_app, sql=test_sql, params={'id': 1})
    return return_success(data)


@db_blueprint.route('/test2', methods=['GET', 'POST'])
def test2():
    """
    调用第二个数据库
    :return:
    """
    test_sql = 'SELECT * FROM history_talk2021.talk_companyids where company_id=:company_id'
    conn = db.get_engine(current_app, bind='history_talk')
    statement = text(test_sql)
    db_result = conn.execute(statement, {'company_id': 72300379})
    data = dbResultToDict(db_result)
    return return_success(data)
