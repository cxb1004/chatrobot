scripts目录下的文件都是以目录为单位，可单独运行，和flask无关

单独运行的两个步骤
1、添加如下代码，用来保证程序运行目录是当前目录
-----------------------------------------------------------
import os
import sys

# 当前目录
basePath = os.path.abspath(os.path.dirname(__file__))
# 设置当前目录为执行运行目录
sys.path.append(basePath)
-----------------------------------------------------------

2、在pyCharm里面，右键点击当前目录
Mark Directories as -> Sources Root
作用是告诉pycharm把当前目录添加为源码的根目录