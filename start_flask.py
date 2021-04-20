# 系统包类
from flask import redirect, url_for
from flask_apscheduler import APScheduler
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from flask_module import init_app, db, init_runserver
# 自定义的包类
from flask_module.config import Config

# 初始化配置
baseConfig = Config()

# 使用配置文件，提取必要的参数，创建Flask App对象
app = init_app()


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('config_blueprint.index'))


# 把flask app托管给Manager
manager = Manager(app)

# 从app的参数里面组装db所需的参数
Migrate(app, db)
# 添加数据迁移的命令到终端脚本工具中
manager.add_command('db', MigrateCommand)

# 从app里面读取相关配置，启动定时任务计划
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

'''
设置runsever(以服务器方式运行)的默认参数，可以被命令行覆盖
     host: 服务器IP地址，0.0.0.0可以被外网访问
     port: 服务器端口号
     use_debugger: 是否使用Werkzeug debugger. 默认False
     use_reloader: 是否自动重新启动服务器，在debug模式下默认是True
     threaded: 是否为每个请求单独起线程,和processes参数互斥
     processes: 发起的进程数量
     passthrough_errors: 不捕捉error，即遇到错误服务器就关闭，默认是False
     ssl_crt: path to ssl certificate file
     ssl_key: path to ssl key file
     options: :func:`werkzeug.run_simple` options.
'''
manager.add_command('runserver', init_runserver())

# 启用数据迁移工具
# Migrate(app, db)
# # 添加数据迁移的命令到终端脚本工具中
# manager.add_command('db', MigrateCommand)

# 运行Flask Manager，启动web服务
if __name__ == '__main__':
    manager.run()
