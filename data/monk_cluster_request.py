import json
import os
import sys
import warnings

from flask_module.corpus_utils import *

# from flask_module.utils import clearCorpusData

warnings.filterwarnings("ignore")
# 以下部分代码可以保证在linux环境下任何目录都可以运行该文件
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

TALK_DATA_FILE = "E:\\快服公司的语料库\\talk_records.txt"
TALK_DATA_REQ = "E:\\快服公司的语料库\\request.txt"

with open(file=TALK_DATA_FILE, mode='r', encoding='utf-8', newline='') as readFile:
    lines = readFile.readlines()
    lines.pop(0)  # 去掉第一行数据

count = 5000
talk_data = []
for line in lines:
    line_data = line.split(sep='\t')
    type = line_data[0]
    talk_id = line_data[1]
    msg = line_data[3].replace('\n', '')
    if isGuestTalk(type):
        talk_data.append(msg)
    if talk_data.__len__() < count:
        continue
    else:
        break

print(talk_data.__len__())

with open(file=TALK_DATA_REQ, mode='w', encoding='utf-8', newline='') as writeFile:
    writeFile.write(json.dumps(talk_data, ensure_ascii=False))
