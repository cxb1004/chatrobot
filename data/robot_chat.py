import json

import requests

URL1 = "http://localhost:8088/robot/service/answer"
params1 = {'rbt_id': '3c5c4a2e-a701-11eb-8557-507b9df05b85', 'question': ''}
URL2 = "http://localhost:8088/robot/service/getAnswerText"
params2 = {'rbt_id': '3c5c4a2e-a701-11eb-8557-507b9df05b85', 'question_id': ''}


def answer():
    question = input("我：")
    if question == '0':
        exit()
    else:
        params = params1.copy()
        params['question'] = question
        res = requests.post(url=URL1, data=params)
        reply_data = json.loads(res.text)
        if reply_data['code'] == 0:
            answers = []
            for reply in reply_data['data']:
                question_id = reply["question_id"]
                params = params2.copy()
                params['question_id'] = question_id
                res2 = requests.post(url=URL2, data=params)
                reply_data2 = json.loads(res2.text)
                a = reply_data2['data']
                answers.append(a)

            print('小块： {}'.format(answers[0]))
            if answers.__len__() > 1:
                print('可能的其它答案：')
                for a in answers:
                    print(a)
        else:
            print("小块无法回答！")


print("=============================")
print("欢迎来到快服公司机器人")
print("使用说明:")
print("输入你想要的提问,按回车结束")
print("输入0,结束整个程序")
print("=============================")
while 1 == 1:
    answer()
