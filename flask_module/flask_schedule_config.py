from apscheduler.jobstores.memory import MemoryJobStore

from flask_module.robot_blueprint.Task.call_scheduled_task import *


class FlaskScheduleConfig:
    # 配置定时任务
    JOBS = [
        # 聚类分析任务，每10分钟执行一次，任务之前执行的数据不同，互不冲突
        # TODO 正式上线的时候，需要开启
        {
            'id': 'cluster_analysis_task',
            'func': call_cluster_analysis_task,
            'args': None,
            'trigger': 'interval',
            'seconds': 3600  # 单位秒，本任务为每1小时执行一次
        }
        # TODO 正式上线的时候，需要开启
        , {
            'id': 'knowledge_update_task',
            'func': call_knowledge_update_task,
            'args': None,
            'trigger': 'interval',
            'seconds': 300  # 单位秒，本任务为每5分钟执行一次
        },
        {
            'id': 'auto_unload_robot_task',
            'func': call_auto_unload_robot_task,
            'args': None,
            'trigger': 'interval',
            'seconds': 3600  # 单位秒，本任务为每1小时执行一次
        }
        # 可以在下面添加自定义任务
        # ,{
        #     'id': 'scheduler_dev_queueing',
        #     'func': task2,
        #     'args': None,
        #     'trigger': {  # 本任务为每周一五点五十九分四十秒执行一次
        #         'type': 'cron',  # 类型
        #         'day_of_week': "0",  # 可定义具体哪几天要执行
        #         'hour': '5',  # 小时数
        #         'minute': '59',
        #         'second': '40'  # "*/3" 表示每3秒执行一次，单独一个"3" 表示每分钟的3秒。现在就是每一分钟的第3秒时循环执行。
        #     }
        # }
    ]
    # 存储位置
    SCHEDULER_JOBSTORES = {
        # 默认任务放在内存中，也可以配置成数据库
        'default': MemoryJobStore()
    }
    # 线程池配置
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }
    # 配置时区
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }
    # 调度器开关
    SCHEDULER_API_ENABLED = True
    SCHEDULER_API_PREFIX = '/schedule'
