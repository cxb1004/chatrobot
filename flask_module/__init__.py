"""
创建Flask App对象，包含如下功能：
1、logging日志功能
2、session、threaded配置
3、数据库配置
4、redis / kafka配置
"""
from flask import Flask, redirect, url_for

from flask_module.config_blueprint import config_blueprint
from flask_module.flask_config import FlaskConfig
from flask_module.flask_log import FlaskLog

proj_config = None
log = FlaskLog()


def init_app():
    log.info('Flask App is initialing...')
    # """初始化创建Flask对象"""
    app = Flask(__name__)

    # 使用配置文件里的数据，生成app的config对象
    app_config = FlaskConfig()

    # 直接从配置文件读取Flask App的相关参数
    app.config.from_object(app_config)

    """
    加载业务模块
    """
    # 加载情感判断模块,设置前置域名为emotion
    app.register_blueprint(config_blueprint, url_prefix='/config')

    log.info('Flask App initial is done')
    return app
