# coding=utf-8

import argparse
from PyGdbDb import PyGdbDb
from ConfigManager import ConfigManager


class PyGDB:
    def __init__(self, project_config_filename):
        # 创建配置文件管理器, 读取配置文件
        self.conf = ConfigManager()
        self.conf.load_project_config(project_config_filename)

        # 从配置文件获取数据库信息
        db_host = self.conf.dict['database']['host']
        db_port = self.conf.dict['database']['port']

        db_db = self.conf.dict['database']['db']
        db_passwd = self.conf.dict['database']['password']
        db_user = self.conf.dict['database']['user']

        # 连接数据库, 创建数据库管理器
        self.db = PyGdbDb(db_host, db_port, db_db, db_user, db_passwd)


if __name__ == "__main__":
    # 配置命令行
    cmd_parser = argparse.ArgumentParser(description="Python-GDB Test Suite")
    cmd_sub_parser = cmd_parser.add_subparsers(title="sub command", dest="sub_cmd")
    parser_test = cmd_sub_parser.add_parser('test', description="haha")
    parser_gendata = cmd_sub_parser.add_parser('gendata', description="Generate data in the basis of config file.")
    parser_gendata.add_argument("filename", help='The name of the config file (in the ./config/ direction.)')
    cmd_args = cmd_parser.parse_args()
    if cmd_args.sub_cmd == "test":
        tester = PyGDB("project_example.yml")
        print("测试!")
    elif cmd_args.sub_cmd == "gendata":
        print("生成! " + cmd_args.filename)
    print "显示内容: " + cmd_args.sub_cmd + "  <----"
else:
    raise Exception("This program isn't a module.")
