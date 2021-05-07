# -*- coding:utf-8 -*-
"""
语料库的一些通用操作
"""
# from bs4 import BeautifulSoup
import re

from bs4 import BeautifulSoup

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
            pattern1 = re.compile(r'(\[' + tag.lower() + '(.*)\])(.*)(\[\/' + tag.lower() + '\])')
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
    去掉快服表情
    :param text:
    :return:
    """
    # 去除{53c_min#xx#}
    pattern = re.compile(r'({53c_min#)(.*)(#})')
    text = pattern.sub(r'', text)
    return text


def removeHtmlTag(text):
    """
    去掉&nbsp
    :param text:
    :return:
    """
    beau = BeautifulSoup(text, 'html.parser')
    # 去除HTML标
    text = beau.get_text()
    text = text.replace('&nbsp;', '').replace('<br/>', '')
    # 去掉因为\xa0 （utf8格式的空格）
    text = "".join(text.split())
    return text


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

# text = '您好，我们是传播易广告投放平台，请问您需要入驻我们的平台吗传播易官网：[url=www.chuanboyi.com]www.chuanboyi.com[/url]入驻我们“传播易”是给你增加了一个销售渠道，相当于你请了10个业务员的，而且我们是零佣金，我们这里注册的广告主快11w了，都是一线广告采购人员，已经入驻传播易的商家他们的销售明显增加，现在都专门安排1-2个人接单把我们传播易当成她主要销售渠道了。个销售1个月的工资，就能抵10个销售1年的销售业绩，老板您，可以算一下这个成本帐我们交易平台每天10wip的流量，有11万的广告主注册。广告采购页面直接显示您的电话和q，直接与客户联系，省去中间环节而且我们的平台的特点是客户源丰富 价格便宜  零佣金 你能否考虑入驻我们的平台呢'
# print(removeHtmlTag(removeEmoj(removeTagContent(text,['url','img']))))
