import logging.handlers

from flask_module.config import Config


class ManageLog:
    __flask_log = None

    def __init__(self):
        _config = Config()
        flask_logger_name = _config.get_value('flask-log', 'flask_logger_manage')
        flask_logger_format = _config.get_value('flask-log', 'flask_logger_format')
        flask_logger_level = logging.getLevelName(_config.get_value('flask-log', 'flask_logger_level'))
        flask_logger_logfile = _config.get_value('flask-log', 'flask_logger_manage_logfile')
        flask_logger_when = _config.get_value('flask-log', 'flask_logger_when')
        flask_logger_interval = int(_config.get_value('flask-log', 'flask_logger_interval'))
        flask_logger_backup_count = int(_config.get_value('flask-log', 'flask_logger_backup_count'))
        flask_logger_encoding = _config.get_value('flask-log', 'flask_logger_encoding')
        """
        静态初始化
        """
        # 内置日志
        ManageLog.__flask_log = logging.getLogger(flask_logger_name)

        # 默认日志配置（日志格式、日志等级）
        __default_formatter = logging.Formatter(flask_logger_format)
        ManageLog.__flask_log.setLevel(flask_logger_level)
        # 默认往控制台输出日志
        __console = logging.StreamHandler()
        __console.setLevel(flask_logger_level)
        __console.setFormatter(__default_formatter)
        ManageLog.__flask_log.addHandler(__console)
        #
        __fileByDateHandle = logging.handlers.TimedRotatingFileHandler(filename=flask_logger_logfile,
                                                                       when=flask_logger_when,
                                                                       interval=flask_logger_interval,
                                                                       backupCount=flask_logger_backup_count,
                                                                       encoding=flask_logger_encoding)
        __fileByDateHandle.setLevel(flask_logger_level)
        __fileByDateHandle.setFormatter(__default_formatter)
        ManageLog.__flask_log.addHandler(__fileByDateHandle)

    @staticmethod
    def info(msg):
        ManageLog.__flask_log.info(msg)

    @staticmethod
    def debug(msg):
        ManageLog.__flask_log.debug(msg)

    @staticmethod
    def warn(msg):
        ManageLog.__flask_log.warning(msg)

    @staticmethod
    def error(msg):
        ManageLog.__flask_log.error(msg)

    @staticmethod
    def error_ex(msg):
        ManageLog.__flask_log.exception(msg, exc_info=True)
