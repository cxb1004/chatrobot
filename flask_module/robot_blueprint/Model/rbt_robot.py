from flask import current_app

from flask_module.robot_blueprint.Model.rbt_knowledge import *
from flask_module.robot_blueprint.constants import RobotConstants
from flask_module.utils import *


class Robot:
    # 机器人自动卸载时间，默认是3600秒（1小时）
    # TODO 这个配置可以写入到配置文件中
    ROBOT_UNLOAD_PERIOD = 3600

    def __init__(self):
        # 机器人ID
        self.__rbt_id = None
        # 语料库，用于文本比较，use_model=0
        self.__corpus = {}
        # 模型，用于模型判断
        self.__model = None
        # 模型判断之后，再使用相似度计算出模型判断的准确值，use_model=0,1
        self.__knowledge = {}
        # 相似度阀值
        self.__sim_idx = 0.0
        # 自动卸载时间
        self.__unloaded_at = None
        # 公司ID
        self.__company_id = None
        # 公司账号
        self.__company_account = None
        # 企业机器人所属行业的行业机器人ID（允许为空）
        self.__industry_robot_id = None

    def assemble(self, rbt_id):
        """
        根据rbt_id组装机器人服务对象
        组装内容包括
        __rbt_id: 机器人ID，直接赋值即可
        __sim_idx: 相似度的阀值，可以从机器人表里面拿，如果没有设置，就从配置文件里面拿默认值
        __knowledge: 用来做前置判断，文本相似度的
        __model: 模型
        __model_knowledge: 全部的知识库，用来给模型判断加精准度指数
        __industry_robot_id：企业机器人所属行业的行业机器人ID
        1、设置rbt_id
        2、根据rbt_id查询机器人信息：rbt_robot表、rbt_industry表联合查询
        3、根据industry_id字段，查询是否有企业机器人ID
        3.1 如果industry_id=None，
        4、
        :param rbt_id:
        :return:
        """
        self.__rbt_id = rbt_id

        # 设置自动卸载时间
        self.__unloaded_at = getRobotUnloadTime(Robot.ROBOT_UNLOAD_PERIOD)

        sql = '''select robot.rbt_id, robot.company_id, robot.company_account, robot.sim_idx,industry.robot_id industry_robot_id from ai_chatrobot.rbt_robot robot left join ai_chatrobot.rbt_industry industry on robot.industry_id=industry.id where robot.rbt_id=:rbt_id and status=:status and type=:type '''
        params = {'rbt_id': rbt_id, 'status': RobotConstants.RBT_STATUS_ON, 'type': RobotConstants.RBT_TYPE_COMPANY}
        queryData = queryBySQL(app=current_app, sql=sql, params=params)
        if queryData.__len__() == 1:
            data = queryData[0]
            self.__company_id = data.get('company_id')
            self.__company_account = data.get('company_account')
            if data.get('company_account') is None:
                self.__sim_idx = float(data.get('company_account'))
            else:
                # TODO 这里后期替换为配置文件的值
                self.__sim_idx = 0.8
            self.__industry_robot_id = data.get('industry_robot_id')

            self.__corpus, self.__knowledge = getKnowledgeDataForAnswer(app=current_app, rbt_id=rbt_id)

            assemble_model(self, rbt_id)
        else:
            # 理论上应该只有一条记录，无记录或是多条记录都是错误的
            errMsg = "机器人{}信息查询失败！".format(rbt_id)
            raise Exception(errMsg)
        pass

    def answer(self, question):
        pass

    def isExpired(self):
        """
        和当前时间相比，机器人是否已经过期
        :return: True 过期  False 未过期
        """
        if self.__unloaded_at is None:
            # 如果没有设置__unloaded_at
            return True
        else:
            # 如果当前时间大于过期时间
            rtn = timeCompareWithNow(self.__unloaded_at)
            if rtn < 1:
                return True
        return False

    def assemble_model(self, rbt_id):
        # TODO 根据rbt_id载入模型
        pass
