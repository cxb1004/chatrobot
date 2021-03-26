from flask_module.config import Config


class FlaskAppConfig:
    cf = Config()

    ENV = cf.get_value('flask-app', 'ENV')
    DEBUG = cf.get_value('flask-app', 'DEBUG')
    TESTING = cf.get_value('flask-app', 'TESTING')
    SESSION_COOKIE_NAME = cf.get_value('flask-app', 'SESSION_COOKIE_NAME')
    SECRET_KEY = cf.get_value('flask-app', 'SECRET_KEY')
    SESSION_PERMANENT = cf.get_value('flask-app', 'SESSION_PERMANENT')
    PERMANENT_SESSION_LIFETIME = cf.get_value('flask-app', 'PERMANENT_SESSION_LIFETIME')
    APPLICATION_ROOT = cf.get_value('flask-app', 'APPLICATION_ROOT')
    SESSION_REFRESH_EACH_REQUEST = cf.get_value('flask-app', 'SESSION_REFRESH_EACH_REQUEST')
    MAX_CONTENT_LENGTH = cf.get_value('flask-app', 'MAX_CONTENT_LENGTH')
    JSON_AS_ASCII = cf.get_value('flask-app', 'JSON_AS_ASCII')
    JSON_SORT_KEYS = cf.get_value('flask-app', 'JSON_SORT_KEYS')
    JSONIFY_PRETTYPRINT_REGULAR = cf.get_value('flask-app', 'JSONIFY_PRETTYPRINT_REGULAR')
    JSONIFY_MIMETYPE = cf.get_value('flask-app', 'JSONIFY_MIMETYPE')

    # SQLALCHEMY_DATABASE_URI = "mysql://root:meidi@122.226.84.37:3306/chat_robot?charset=utf8mb4"
    # # 动态追踪修改设置，如未设置只会提示警告
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # # 查询时会显示原始SQL语句
    # SQLALCHEMY_ECHO = True
