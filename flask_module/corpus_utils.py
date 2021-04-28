"""
语料库的一些通用操作
"""

"""
对于聊天数据的类型区分
type	含义	             客服	访客
a	快问快答（答）	      ✔	
b	繁忙提示语	          ✔	
e   关闭网页               ✔
g	访客消息		                 ✔
h	接通提示语	          ✔	
j	智能引导	              ✔	
k	快捷提问		                 ✔
l	访客留言		                 ✔
m	场景引导	              ✔	
o	退出挽留		                 ✔
p	客服消息	              ✔	
q	快问快答（问）		         ✔
r	客服留言	              ✔	
u	机器人	              ✔	
w	微信预约消息	          ✔	
z	访客填写快捷表单		         ✔
"""

def isGuestTalk(type):
    if type in ['g','l','k','o','q','z']:
        return True
    else:
        return False

def clearCorpusData(text):
    """
    对数据进行清洗，过滤到一部分不需要分析的数据，比如表情符号，电话号码等
    :param text:
    :return:
    """
    return text
