from flask_module.utils import *


class Robot:
    # 机器人自动卸载时间，默认是3600秒（1小时）
    # TODO 这个配置可以写入到配置文件中
    ROBOT_UNLOAD_PERIOD = 3600

    def __init__(self, rbtID=None, simIdx=None):
        # 这里只定义机器人服务中必须用到的属性，其它信息可在detail函数中获取
        # 机器人ID
        self.__rbt_id = None
        # 知识库，用于文本比较
        self.__knowledge = {}
        # 模型，用于模型判断
        self.__model = None
        # 相似度法制
        self.__sim_idx = 0.9
        # 自动卸载时间
        self.__unloaded_at = getRobotUnloadTime(Robot.ROBOT_UNLOAD_PERIOD)

        if rbtID is not None:
            self.__rbt_id = rbtID
        if simIdx is not None:
            self.__sim_idx = simIdx

    def __str__(self):
        return self.detail(self)

    def detail(self):
        """
        获得机器人详细信息
        :return:
        """
        msg = "robot id = {}".format(self.__rbt_id)
        return msg

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
