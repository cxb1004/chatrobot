from flask import current_app, request

from flask_module.db_utils import *
from flask_module.log_manage import ManageLog as mlog
from flask_module.result_json import *
from flask_module.robot_blueprint import robot_blueprint
from flask_module.robot_blueprint.constants import RobotConstants
from flask_module.utils import *


@robot_blueprint.route('/manager/getIndustryList', methods=['POST'])
def get_industry_list():
    """
    直接获得行业列表（一二级）
    :return:
    """
    sql = 'select id, industry_name, industry_parent from cloud_customer_service.ccs_industry AS industry order by industry_parent,id asc'
    try:
        industry_list = queryBySQL(app=current_app, sql=sql)
    except Exception as ex:
        mlog.error_ex("执行sql出错：{}".format(sql))
        return return_fail("执行sql出错")
    return return_success(industry_list)


@robot_blueprint.route('/manager/getDefaultIndustryByCompany', methods=['POST'])
def get_default_industry_by_company():
    """
    获得企业默认所属的行业
    :return:
    """
    company_id = request.form.get('company_id', type=int)
    sql = '''
            SELECT 
                customer.company_id,
                customer.company_name,
                industry1.id industry_id_1,
                industry1.industry_name as industry_name_1,
                customer.industry industry_id_2,
                industry2.industry_name as industry_name_2
            FROM
                cloud_customer_service.ccs_active_customer AS customer,
                cloud_customer_service.ccs_industry AS industry1,
                cloud_customer_service.ccs_industry AS industry2
            WHERE
                1=1
                AND customer.company_id = :company_id
                and customer.industry = industry2.id
                and industry2.industry_parent = industry1.id
        '''
    try:
        industry_list = queryBySQL(app=current_app, sql=sql, params={'company_id': company_id})
    except Exception as ex:
        mlog.error_ex("执行sql出错：{}".format(sql))
        return return_fail("执行sql出错")
    return return_success(industry_list)


@robot_blueprint.route('/manager/createCompanyRobot', methods=['POST'])
def create_company_robot():
    """
    创建企业机器人
    1、 验证参数
    2、确认行业数据是一级行业，如果不是，自动查询出一级行业
    3、如果一级行业不存在，就自动创建
    4、检查这个企业是否已经有过，如果已经创建过，返回异常
    5、如果没有创建过同类机器人，创建机器人
    :return:
    """
    # 接收参数
    company_id = request.form.get('company_id', type=int)
    company_account = request.form.get('company_account', type=str)
    industry_name = request.form.get('industry_name', type=str)
    expired_date_txt = request.form.get('expired_date', type=str)
    rbt_name = request.form.get('rbt_name', type=str)

    # 1、 验证参数
    if isNullOrBlank(company_id) or isNullOrBlank(company_account) or isNullOrBlank(industry_name) or isNullOrBlank(
            expired_date_txt):
        return return_fail("参数缺失！")
    try:
        expired_date = strToDate(expired_date_txt)
    except Exception as ex:
        return return_fail('过期日格式错误：yyyy-mm-dd')

    mlog.info('开始创建机器人...')

    # 2、确认行业数据是一级行业，如果不是，自动查询出一级行业
    # 判断是否是一级行业
    sql = '''select count(1) cnt from cloud_customer_service.ccs_industry AS industry where industry_name = :industry_name and industry_parent is null'''
    count = countBySQL(app=current_app, sql=sql, params={'industry_name': industry_name})
    if count == 0:
        # 非一级行业，通过parent查询一级行业
        sql = '''
            SELECT 
                industry2.industry_name
            FROM
                cloud_customer_service.ccs_industry AS industry1,
                cloud_customer_service.ccs_industry AS industry2
            WHERE
                industry1.industry_name = :industry_name
                    AND industry1.industry_parent = industry2.id
        '''
        queryData = queryBySQL(app=current_app, sql=sql, params={'industry_name': industry_name})
        if queryData is None or queryData.__len__() == 0:
            # 如果还是找不到，就说明行业数据有问题了，需要抛出异常返回了
            errMsg = "行业名不是一级行业，请确认行业数据【{}】是否正确！".format(industry_name)
            mlog.error(errMsg)
            return return_fail(errMsg)
        else:
            industry_name = queryData[0].get('industry_name')
    mlog.debug('验证出一级行业为：{}'.format(industry_name))

    # 3、如果一级行业不存在，就自动创建
    sql = 'select id from rbt_industry where industry_name=:industry_name'
    queryData = queryBySQL(app=current_app, sql=sql, params={'industry_name': industry_name})
    count = queryData.__len__()
    if count == 0:
        mlog.info('行业【{}】不存在，新建行业...'.format(industry_name))
        sql2 = '''
            INSERT INTO rbt_industry
                (industry_name,
                has_model,
                robot_id,
                created_at,
                updated_at,
                deleted_at)
                VALUES
                (:industry_name,
                :has_model,
                null,
                now(),
                now(),
                null)
        '''
        params2 = {'industry_name': industry_name,
                   'has_model': RobotConstants.INDUSTRY_MODEL_NO_EXIST
                   }
        executeBySQL(app=current_app, sql=sql2, params=params2)
        mlog.info('行业【{}】创建成功，稍后需要运营为这个行业训练模型'.format(industry_name))

        # 创新之后重新获取industry_id
        queryData = queryBySQL(app=current_app, sql=sql, params={'industry_name': industry_name})

    # 获得industry_id
    industry_id = int(queryData[0].get('id'))
    mlog.debug('行业【{}】已经存在:industry_id = {}'.format(industry_name, industry_id))

    # 4、检查这个企业是否已经有过，如果已经创建过，返回异常
    sql = '''select count(rbt_id) as cnt from rbt_robot where company_id=:company_id and type=:type and status=:status and industry_id=:industry_id'''
    params = {'company_id': company_id,
              'type': RobotConstants.RBT_TYPE_COMPANY,
              'status': RobotConstants.RBT_STATUS_ON,
              'industry_id': industry_id
              }
    count = countBySQL(app=current_app, sql=sql, params=params)
    if count > 0:
        errMsg = '企业【{}】已经创建过同行业的机器人，无法重复创建！'.format(company_id)
        mlog.error(errMsg)
        return return_fail(errMsg)
    else:
        # 5、如果没有创建过同类机器人，创建机器人
        rbt_id = getUUID_1()
        if isNullOrBlank(rbt_name):
            rbt_name = rbt_id

        sql = '''INSERT INTO ai_chatrobot.rbt_robot (rbt_id, rbt_name, type, company_id, company_account, industry_id, 
        industry_name, status, model_status, model_updated_at, expired_at, created_at, updated_at, deleted_at) 
        VALUES (:rbt_id, :rbt_name, :type, :company_id, :company_account, :industry_id, :industry_name, :status, 
        :model_status, :model_updated_at, :expired_at, now(), null, null)'''
        params = {
            'rbt_id': rbt_id,
            'rbt_name': rbt_name,
            'type': RobotConstants.RBT_TYPE_COMPANY,
            'company_id': company_id,
            'company_account': company_account,
            'industry_id': industry_id,
            'industry_name': industry_name,
            'status': RobotConstants.RBT_STATUS_ON,
            'model_status': RobotConstants.RBT_MODEL_STATUS_EMPTY,
            'model_updated_at': None,
            'expired_at': expired_date,
        }
        executeBySQL(app=current_app, sql=sql, params=params)
        mlog.info('企业机器人创建成功：{}'.format(rbt_id))
        return return_success({'rbt_id': rbt_id})


@robot_blueprint.route('/manager/getRobotListByCompany', methods=['POST'])
def get_robot_list_by_company():
    # 接收参数
    company_id = request.form.get('company_id', type=int)
    current_page = request.form.get('current_page', type=int)
    per_page = request.form.get('per_page', type=int)

    if isNullOrBlank(current_page) or isNullOrBlank(per_page):
        return_fail('参数缺失！')

    sql = '''select count(rbt_id) cnt from ai_chatrobot.rbt_robot where company_id=:company_id and deleted_at is null'''
    params = {'company_id': company_id}
    all_records = countBySQL(app=current_app, sql=sql, params=params)

    maxPage, start, offset = calculatePageParameters(all_records, per_page, current_page)

    sql = '''select rbt_id, rbt_name, type, company_id, company_account, industry_id, industry_name, status, model_status, model_updated_at, expired_at, created_at, updated_at, deleted_at from ai_chatrobot.rbt_robot where company_id=:company_id and deleted_at is null order by updated_at desc, created_at desc, status desc limit :start,:offset'''
    params = {'company_id': company_id, 'start': start, 'offset': offset}
    queryData = queryBySQL(app=current_app, sql=sql, params=params)

    return return_success(queryData)


@robot_blueprint.route('/manager/getRobotList', methods=['POST'])
def get_robot_list():
    # 接收参数
    current_page = request.form.get('current_page', type=int)
    per_page = request.form.get('per_page', type=int)

    if isNullOrBlank(current_page) or isNullOrBlank(per_page):
        return_fail('参数缺失！')

    sql = '''select count(rbt_id) cnt from ai_chatrobot.rbt_robot where deleted_at is null'''
    all_records = countBySQL(app=current_app, sql=sql)

    maxPage, start, offset = calculatePageParameters(all_records, per_page, current_page)

    sql = '''select rbt_id, rbt_name, type, company_id, company_account, industry_id, industry_name, status, model_status, model_updated_at, expired_at, created_at, updated_at, deleted_at from ai_chatrobot.rbt_robot where deleted_at is null order by updated_at desc, created_at desc, status desc limit :start,:offset'''
    params = {'start': start, 'offset': offset}
    queryData = queryBySQL(app=current_app, sql=sql, params=params)

    return return_success(queryData)


@robot_blueprint.route('/manager/syncKnowledgeFull', methods=['POST'])
def sync_knowledge_full():
    return return_success('')


@robot_blueprint.route('/manager/syncKnowledgePartial', methods=['POST'])
def sync_knowledge_partial():
    return return_success('')
