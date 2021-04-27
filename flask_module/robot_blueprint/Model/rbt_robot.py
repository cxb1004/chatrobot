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

        sql = '''select robot.rbt_id, robot.company_id, robot.company_account, robot.sim_idx,industry.robot_id industry_robot_id from ai_chatrobot.rbt_robot robot left join ai_chatrobot.rbt_industry industry on robot.industry_id=industry.id where robot.rbt_id=:rbt_id and status=:status and type=:type and robot.deleted_at is null'''
        params = {'rbt_id': rbt_id, 'status': RobotConstants.RBT_STATUS_ON, 'type': RobotConstants.RBT_TYPE_COMPANY}
        queryData = queryBySQL(app=current_app, sql=sql, params=params)
        if queryData.__len__() == 1:
            data = queryData[0]
            self.__company_id = data.get('company_id')
            self.__company_account = data.get('company_account')
            if data.get('sim_idx') is None:
                self.__sim_idx = float(data.get('sim_idx'))
            else:
                # TODO 这里后期替换为配置文件的值
                self.__sim_idx = 0.4
            self.__industry_robot_id = data.get('industry_robot_id')

            self.__corpus, self.__knowledge = getKnowledgeDataForAnswer(app=current_app, rbt_id=rbt_id)
            # 模型组装功能代做
            self.assemble_model(rbt_id)
        else:
            # 理论上应该只有一条记录，无记录或是多条记录都是错误的
            errMsg = "组建机器人失败: 机器人[{}]不存在".format(rbt_id)
            raise Exception(errMsg)

    def answer(self, simUtil, question):
        """
        机器人回复接口
        1、检查语料库是否存在
        2、如果语料库存在就进行文本判断，记录满足条件的question_id, idx_val,type,tag
        3、如果语料库不存在，就检查企业模型是否存在
        4、如果企业模型存在，就进行模型判断
        4.1 模型判断得出question_id之后，对question_id说对应文本，进行文本匹配度的判断,得出一个相似度值，代表这个判断的准确度
        5、如果既没有知识库，又没有模型，抛出异常
        :param simUtil:
        :param question:
        :return:
        """
        if (self.__corpus.__len__() == 0 or self.__corpus is None) and self.__model is None:
            # 5、如果既没有知识库，又没有模型，抛出异常
            raise Exception("机器人无知识库，无模型，无法回答！")

        company_answer = []
        # 1、检查语料库是否存在
        if self.__corpus.__len__() > 0:

            for sentence in self.__corpus.keys():
                temp_dict = {}
                simValue = simUtil.getSimilarityIndex(question, sentence)
                print("相似值：{}   比较语句：{}".format(simValue, sentence))
                if simValue >= self.__sim_idx:
                    temp_dict['question_id'] = self.__corpus.get(sentence)
                    temp_dict['sim_value'] = simValue
                    temp_dict['type'] = RobotConstants.ANSWER_TYPE_KNOWLEDGE
                    temp_dict['tag'] = RobotConstants.ANSWER_TAG_COMPANY
                    # 2、如果语料库存在就进行文本判断，记录满足条件的question_id, idx_val, type, tag
                    company_answer.append(temp_dict)

        # TODO  3、检查企业模型是否存在
        if self.__model is not None:
            # 4.1 模型判断得出question_id之后，对question_id说对应文本，进行文本匹配度的判断, 得出一个相似度值，代表这个判断的准确度
            temp_dict = {}
            # TODO 这里要修改成使用模型,获得预测数据：question_id
            # question_id = self.__model.pred(question)
            question_id = "xxxxxxx"
            # 根据question_id获得question文本
            pred_question = self.__knowledge.get(question_id).get('question')
            sim_value = simUtil.getSimilarityIndex(question, pred_question)
            temp_dict['question_id'] = question_id
            temp_dict['sim_val'] = sim_value
            temp_dict['type'] = RobotConstants.ANSWER_TYPE_MODEL
            temp_dict['tag'] = RobotConstants.ANSWER_TAG_COMPANY
            company_answer.append(temp_dict)
        # 对企业机器人的答案，按相似度从高到低排序，并获取一定的数量值
        answers = self.sortAndLimit(company_answer)
        return answers

    def sortAndLimit(self, answer_list):
        """
        对企业机器人的答案，按相似度从高到低排序，并获取一定的数量值
        :return:
        """
        answer_list.sort(key=lambda i: i['sim_value'], reverse=True)
        # TODO 这里的5，可以从配置文件里面读取
        if answer_list.__len__()>5:
            return answer_list[:5]
        else:
            return answer_list

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

    def getIndustryRobotID(self):
        return self.__industry_robot_id
