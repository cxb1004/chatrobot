class FlaskConfig():
    # 调试模式
    DEBUG = False
    # 配置日志
    LOG_LEVEL = "INFO"

    # 设置密钥，可以通过 base64.b64encode(os.urandom(48)) 来生成一个指定长度的随机字符串
    # 开启session功能设置secret_key
    SECRET_KEY = "12345653KF654321"

    # __user = cf.get('Mysql-Database', 'user'),
    # __password = cf.get('Mysql-Database', 'password'),
    # __host = cf.get('Mysql-Database', 'host'),
    # __port = cf.get('Mysql-Database', 'port'),
    # __database = cf.get('Mysql-Database', 'database'),
    # __charset = cf.get('Mysql-Database', 'charset'),
    # __log_path = cf.get('Logger-path', 'log_path'),
    # __environment = cf.get('Run-environment', 'environment'),
    #
    #
    # """Mysql"""
    # user = __user[0]
    # password = __password[0]
    # host = __host[0]
    # port = __port[0]
    # database = __database[0]
    # charset = __charset[0]
    #
    # """日志目录"""
    # log_path = __log_path[0]
    #
    # """运行环境"""
    # environment = __environment[0]