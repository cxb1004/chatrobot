from flask import Blueprint

db_blueprint = Blueprint('db_blueprint', __name__)

# 这一句必须放在Blueprint()之下，否则会出现ImportError: cannot import name 'xxx_blueprint' 的错误
from flask_module.db_blueprint import db_info
