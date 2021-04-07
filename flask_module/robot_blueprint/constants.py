class RobotConstants:
    """
    用于设置机器人模块中使用到的常量，规范各类常量的定义
    """

    # =============机器人的状态=============
    # 启用
    RBT_STATUS_ON = 1
    # 禁用
    RBT_STATUS_OFF = 0

    # =============机器人的类型=============
    # 企业机器人
    RBT_TYPE_COMPANY = 0
    # 行业机器人
    RBT_TYPE_INDUSTRY = 1
    # 通用机器人
    RBT_TYPE_COMMON = 2
    # =============机器人模型的类型=============
    # 模型为空（一般是机器人刚创建的时候）
    RBT_MODEL_STATUS_EMPTY = 0
    # 
    RBT_MODEL_STATUS_TRAINING = 0
    RBT_MODEL_STATUS_TEST = 0
    RBT_MODEL_STATUS_DEPLOY = 0
