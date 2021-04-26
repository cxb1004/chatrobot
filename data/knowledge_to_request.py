"""
这个方法是把拿到的某个企业知识库的数据（全库）
转化为chatrobot接口可以接受的data（json），然后通过接口进行数据上传

获取数据的接口：
地址：https://newknowledgebase.53kf.com/newknowledgebase/selectCompanyQABase/selectPrimaryIndustry
参数： {'token': 'Aj|uU620cjJ`53kf', 'company_id': 72000079}

chatrobot数据接口：
url: http:localhost:8088/robot/manager/syncKnowledge
参数：{'rbt_id':'7b4c86d8-9dae-11eb-b73b-2c6e85a3b49d', 'is_overwrite':1, "data":?}

"""
import json
import os
import sys
import warnings

import requests

warnings.filterwarnings("ignore")
# 以下部分代码可以保证在linux环境下任何目录都可以运行该文件
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

url = 'https://newknowledgebase.53kf.com/newknowledgebase/selectCompanyQABase/selectPrimaryIndustry'
post_params = {'token': 'Aj|uU620cjJ`53kf', 'company_id': 72000079}
res = requests.post(url=url, data=post_params)
res_json = json.loads(res.text)
print(res_json)

post_request_data = []
if int(res_json['code']) == 101:
    knowledges = res_json['data']
    for knowledge in knowledges:
        company_id = knowledge['company_id']
        knowledge_id = knowledge['knowledge_id']
        answer = knowledge['answer']
        question = knowledge['question']
        category_id = knowledge['category_id']
        parent_id = knowledge['parent_id']

        knowledge_data = {}
        knowledge_data['id'] = knowledge_id
        knowledge_data['company_id'] = company_id
        knowledge_data['question'] = question
        knowledge_data['answer'] = answer
        knowledge_data['category_id'] = category_id
        knowledge_data['parent_id'] = parent_id
        knowledge_data['action'] = 'add'

        post_request_data.append(knowledge_data)
else:
    print('接口调用失败：{}'.res_json.get['message'])

print(post_request_data)