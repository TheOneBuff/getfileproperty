# coding: utf-8
import os
import sys
import time
import configparser

# ./ 表示当前目录，../表示上级目录 /表示根目录
file = './config.ini'

# 创建配置文件对象
con = configparser.ConfigParser()
# 读取文件
con.read(file, encoding='utf-8')
# 文件路径
filepath = con.items('path')

if __name__ == '__main__':
    path = filepath[0][1] + "\\" + time.strftime("%Y-%m-%d", time.localtime()).replace("-", "") + "_ETF_SecurityInfos.csv"
    fileproperty = os.stat(path)
    # 文件大小
    #print(fileproperty.st_size)
    if fileproperty.st_size > 0:
        print("File exists")
        sys.exit(0)
    else:
        print("File does not exist")
        sys.exit(-1)
