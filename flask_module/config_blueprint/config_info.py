from flask import current_app

from flask_module.config_blueprint import config_blueprint


@config_blueprint.route('/', methods=['GET', 'POST'])
def index():
    return 'the flask server is running normally...'


@config_blueprint.route('/detail', methods=['GET', 'POST'])
def detail():
    app_config_info = 'Flask Web App configuration: '
    for key in current_app.config.keys():
        config_info = '\n  {} : {}'.format(key, current_app.config.get(key))
        app_config_info = app_config_info + config_info
    return app_config_info


# from flask_module import db
#
#
# @config_blueprint.route('/db', methods=['GET', 'POST'])
# def db_check():
#     engine = db.get_engine()
#     sql = "select count(*) from information_schema.tables where table_schema='chat_robot'"
#     result_obj = engine.execute(statement=sql)
#     return result_obj
