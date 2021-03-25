class FlaskConfig():
    # 调试模式
    DEBUG = False
    # 配置日志
    LOG_LEVEL = "INFO"

    # 设置密钥，可以通过 base64.b64encode(os.urandom(48)) 来生成一个指定长度的随机字符串
    # 开启session功能设置secret_key
    SECRET_KEY = "12345653KF654321"

    SQLALCHEMY_DATABASE_URI = "mysql://root:meidi@122.226.84.37:3306/chat_robot?charset=utf8mb4"
    # 动态追踪修改设置，如未设置只会提示警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = True
