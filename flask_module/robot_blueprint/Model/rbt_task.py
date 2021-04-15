from flask_module.db_utils import *
from flask_module.utils import *


class RobotTask:
    STATUS_INIT = 0
    TYPE_SYNC_KNOWLEDGE = {'type': 1, 'task': '更新知识库'}

    def __init__(self):
        self.task_id = None
        self.task = None
        self.type = None
        self.company_id = None
        self.rbt_id = None
        self.status = None
        self.comment = None
        self.created_at = None
        self.updated_at = None

    def setProps(self, task_id=None, task=None, type=None, company_id=None, rbt_id=None, status=None, comment=None,
                 created_at=None, updated_at=None):
        self.task_id = task_id
        self.task = task
        self.type = type
        self.company_id = company_id
        self.rbt_id = rbt_id
        self.status = status
        self.comment = comment
        self.created_at = created_at
        self.updated_at = updated_at


def createTask(app=None, sess=None, company_id=None, rbt_id=None, task_type=None, comment=None):
    type = task_type.get('type')
    task = task_type.get('task')

    sql = '''INSERT INTO ai_chatrobot.rbt_task (task_id, task, type, company_id, rbt_id, status, comment, created_at, updated_at) VALUES (:task_id, :task, :type, :company_id, :rbt_id, :status, :comment, now(), null)'''
    params = {
        'task_id': getUUID_1(),
        'task': task,
        'type': type,
        'company_id': company_id,
        'rbt_id': rbt_id,
        'status': RobotTask.STATUS_INIT,
        'comment': comment
    }
    effect_count = executeBySQL(app=app, sess=sess, sql=sql, params=params)

    return effect_count


def updateTaskStatus():
    pass


def queryTask(app=None, sess=None, rbt_id=None):
    pass


def getTaskList(app=None, sess=None):
    """
    查询task数据
    :param app:
    :param sess:
    :return:
    """
    sql = '''SELECT rbt_task.task_id, rbt_task.task, rbt_task.type, rbt_task.company_id, rbt_task.rbt_id, rbt_task.status, rbt_task.comment, rbt_task.created_at, rbt_task.updated_at FROM ai_chatrobot.rbt_task order by updated_at desc, created_at desc'''
    query_data = queryBySQL(app=app, sess=sess, sql=sql)
    return query_data
