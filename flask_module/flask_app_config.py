from flask_module.config import Config
from flask_module.utils import strToBool

DATABASE_CONNECTION_STRING = 'mysql://{}:{}@{}:{}/{}?charset=utf8mb4'

class FlaskAppConfig:
    cf = Config()

    ENV = cf.get_value('flask-app', 'ENV')
    DEBUG = strToBool(cf.get_value('flask-app', 'DEBUG'))
    TESTING = strToBool(cf.get_value('flask-app', 'TESTING'))
    SESSION_COOKIE_NAME = cf.get_value('flask-app', 'SESSION_COOKIE_NAME')
    SECRET_KEY = cf.get_value('flask-app', 'SECRET_KEY')
    SESSION_PERMANENT = strToBool(cf.get_value('flask-app', 'SESSION_PERMANENT'))
    PERMANENT_SESSION_LIFETIME = cf.get_value('flask-app', 'PERMANENT_SESSION_LIFETIME')
    APPLICATION_ROOT = cf.get_value('flask-app', 'APPLICATION_ROOT')
    SESSION_REFRESH_EACH_REQUEST = strToBool(cf.get_value('flask-app', 'SESSION_REFRESH_EACH_REQUEST'))
    MAX_CONTENT_LENGTH = int(cf.get_value('flask-app', 'MAX_CONTENT_LENGTH'))
    JSON_AS_ASCII = strToBool(cf.get_value('flask-app', 'JSON_AS_ASCII'))
    JSON_SORT_KEYS = strToBool(cf.get_value('flask-app', 'JSON_AS_ASCII'))
    JSONIFY_PRETTYPRINT_REGULAR = strToBool(cf.get_value('flask-app', 'JSONIFY_PRETTYPRINT_REGULAR'))
    JSONIFY_MIMETYPE = cf.get_value('flask-app', 'JSONIFY_MIMETYPE')

    # 以下是主数据库配置
    SQLALCHEMY_DATABASE_URI = DATABASE_CONNECTION_STRING.format(
        cf.get_value('flask-sqlalchemy', 'user'),
        cf.get_value('flask-sqlalchemy', 'password'),
        cf.get_value('flask-sqlalchemy', 'host'),
        cf.get_value('flask-sqlalchemy', 'port'),
        cf.get_value('flask-sqlalchemy', 'database')
    )
    SQLALCHEMY_ECHO = strToBool(cf.get_value('flask-sqlalchemy', 'ECHO'))
    SQLALCHEMY_TRACK_MODIFICATIONS = strToBool(cf.get_value('flask-sqlalchemy', 'TRACK_MODIFICATIONS'))
    SQLALCHEMY_POOL_SIZE = int(cf.get_value('flask-sqlalchemy', 'POOL_SIZE'))
    SQLALCHEMY_POOL_TIMEOUT = int(cf.get_value('flask-sqlalchemy', 'POOL_SIZE'))
    SQLALCHEMY_POOL_RECYCLE = int(cf.get_value('flask-sqlalchemy', 'POOL_RECYCLE'))
    SQLALCHEMY_MAX_OVERFLOW = int(cf.get_value('flask-sqlalchemy', 'MAX_OVERFLOW'))
    SQLALCHEMY_ENGINE_OPTIONS: {}
    # 用于绑定多个数据库，配置方法参见：http://www.pythondoc.com/flask-sqlalchemy/binds.html#binds
    SQLALCHEMY_BINDS = {
        'history_talk': DATABASE_CONNECTION_STRING.format(
            cf.get_value('flask-sqlalchemy-talk', 'user'),
            cf.get_value('flask-sqlalchemy-talk', 'password'),
            cf.get_value('flask-sqlalchemy-talk', 'host'),
            cf.get_value('flask-sqlalchemy-talk', 'port'),
            cf.get_value('flask-sqlalchemy-talk', 'database')
        ),
        'ccs': DATABASE_CONNECTION_STRING.format(
            cf.get_value('flask-sqlalchemy-ccs', 'user'),
            cf.get_value('flask-sqlalchemy-ccs', 'password'),
            cf.get_value('flask-sqlalchemy-ccs', 'host'),
            cf.get_value('flask-sqlalchemy-ccs', 'port'),
            cf.get_value('flask-sqlalchemy-ccs', 'database')
        ),
    }

