from flask import Blueprint

robot_blueprint = Blueprint('robot_blueprint', __name__)

# 这一句必须放在Blueprint()之下，否则会出现ImportError: cannot import name 'xxx_blueprint' 的错误
from flask_module.robot_blueprint import robot_train, robot_service, robot_manage
