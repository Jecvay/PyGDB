# coding=utf-8

import os

"""
    公用方法
"""

"""
    日志
    level: 级别
    msg: 信息
"""
log_limit_level = 2
def log(level, msg, limit_level=log_limit_level):
    if 2-level > log_limit_level:
        return
    if level == 0:      # [info]
        print "[info] " + str(msg)
    elif level == 1:
        print "[warn] " + str(msg)
    elif level == 2:
        print "[error] " + str(msg)
        exit()


"""
    编译 C 程序
    file_path: 文件路径
    compile_args: 编译参数
"""
def compile(file_path, compile_args):
    log(0, '正在编译: ' + file_path)

"""
    判断文件是否存在
"""
def exist_file(file_path):
    return os.path.exists(file_path)