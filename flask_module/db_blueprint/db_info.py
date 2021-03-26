from flask import current_app

from flask_module import db
from flask_module.db_blueprint import db_blueprint


@db_blueprint.route('/', methods=['GET', 'POST'])
def index():
    # 【重要提示】如果运行出现ModuleNotFoundError: No module named 'MySQLdb'错误
    # 是需要flask_module.__init__.py文件里面运行pymysql.install_as_MySQLdb()
    eng = db.get_engine(current_app)

    return 'the db server is running normally...'
