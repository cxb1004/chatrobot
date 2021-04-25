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
    # 模型训练中
    RBT_MODEL_STATUS_TRAINING = 0
    # 模型训练完成，测试中
    RBT_MODEL_STATUS_TEST = 0
    # 模型
    RBT_MODEL_STATUS_DEPLOY = 0

    # =============行业是否存在模型=============
    # 存在
    INDUSTRY_MODEL_EXIST = 1
    # 不存在
    INDUSTRY_MODEL_NO_EXIST = 0

    # =============知识库中的知识，使用模型是否预测准确=============
    # 模型预测失败
    KNOWLEDGE_USE_MODEL_NO_PASS = 0
    # 模型预测成功
    KNOWLEDGE_USE_MODEL_PASS = 1

    # =============问答=============
    # 给出答案是通过模型m
    ANSWER_TYPE_MODEL = 'm'
    # 给出答案是通过知识库k
    ANSWER_TYPE_KNOWLEDGE = 'k'
    # 给出答案的是企业知识库
    ANSWER_TAG_COMPANY = 'c'
    # 给出答案的是行业知识库
    ANSWER_TAG_INDUSTRY = 'i'
