"""
创建Flask App对象，包含如下功能：
1、web服务器的配置（ok）
1、logging日志功能
2、session、threaded配置
3、数据库配置
4、redis / kafka配置
"""
import pymysql
from flask import Flask
from flask_script import Server
from flask_sqlalchemy import SQLAlchemy

# 【重要提示】如果运行出现ModuleNotFoundError: No module named 'MySQLdb'错误
# 是需要flask_module.__init__.py文件里面运行pymysql.install_as_MySQLdb()
pymysql.install_as_MySQLdb()

from flask_module.config import Config
from flask_module.config_blueprint import config_blueprint
from flask_module.flask_app_config import FlaskAppConfig
from flask_module.flask_log import FlaskLog
from flask_module.utils import strToBool

proj_config = None
log = FlaskLog()
baseConfig = Config()
# 使用配置文件里的数据，生成app的config对象
flask_app_config = FlaskAppConfig()

db = SQLAlchemy()
from flask_module.db_blueprint import db_blueprint


def init_app():
    log.info('Flask App is initialing...')

    # 初始化创建Flask对象
    app = Flask(__name__)

    # 直接从配置文件读取Flask App的相关参数
    app.config.from_object(flask_app_config)

    # SQLAlchemy读取app里面的配置信息，对数据库进行初始化
    db.init_app(app)

    """
    加载业务模块
    """
    # 加载情感判断模块,设置前置域名为emotion
    app.register_blueprint(config_blueprint, url_prefix='/config')
    app.register_blueprint(db_blueprint, url_prefix='/db')

    log.info('Flask App initial is done')
    return app


def init_runserver():
    return Server(host=baseConfig.get_value('flask-runserver', 'host'),
                  port=baseConfig.get_value('flask-runserver', 'port'),
                  use_debugger=strToBool(baseConfig.get_value('flask-runserver', 'use_debugger')),
                  use_reloader=strToBool(baseConfig.get_value('flask-runserver', 'use_reloader')),
                  threaded=strToBool(baseConfig.get_value('flask-runserver', 'threaded')),
                  passthrough_errors=strToBool(baseConfig.get_value('flask-runserver', 'passthrough_errors'))
                  )
