"""
语料库的一些通用操作
"""
# from bs4 import BeautifulSoup
import re

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
    if type in ['g', 'l', 'k', 'o', 'q', 'z']:
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


def removeTagContent(text, tags):
    """
    去掉IMG标签
    :param tags: 需要移除的表情
    :param text:
    :return:
    """
    if tags.__len__() > 0:
        text = text.lower()
        for tag in tags:
            pattern1 = re.compile(r'(\[' + tag.lower() + '\])(.*)(\[\/' + tag.lower() + '\])')
            text = pattern1.sub(r'', text)
    return text


def removeQQ_Email_Phone_Mobile(text):
    """
    去掉已经可以识别的标签
    :param text:
    :return:
    """
    tags = ['mobile', 'phone', 'email', 'qq']
    text = removeTagContent(text, tags)
    return text


def removeEmoj(text):
    """
    去掉已经可以识别的标签
    :param text:
    :return:
    """
    # 去除{53c_min#xx#}
    pattern = re.compile(r'({53c_min#)(.*)(#})')
    text = pattern.sub(r'', text)

# def clear_content(text):
#     """
#     对文本进行清洗
#     1、去除html标签
#     2、去除[img]
#     3、去除自定义的表情符号 {53c_min#xx#}
#
#     :param text: 文本
#     :return: 去除html标签
#     """
#     beau = BeautifulSoup(text)
#     # 去除HTML标
#     new_text = beau.get_text()
#
#     # 涉及语义的英文字符替换成中文的
#     new_text = new_text.replace('?', '？')
#     new_text = new_text.replace('!', '！')
#
#     return new_text
#
