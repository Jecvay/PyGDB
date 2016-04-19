# coding=utf-8

import argparse
import PyGdbUtil
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

    # 结束项目
    def release_project(self):
        self.db.connection.close()

    # 显示项目信息
    def print_project_info(self):
        print '------------------------------'
        print '    项目名称: ' + self.conf.pro_name
        print '    数据表前缀: ' + self.conf.pro_table_prefix
        print '------------------------------'



if __name__ == "__main__":
    # 配置命令行解析器
    cmd_parser = argparse.ArgumentParser(description="Python-GDB Test Suite")
    cmd_sub_parser = cmd_parser.add_subparsers(title="sub command", dest="sub_cmd")     # 子解析器
    parser_test = cmd_sub_parser.add_parser('test', description="haha")     # 测试子程序
    parser_gendata = cmd_sub_parser.add_parser('gendata', description="Generate data in the basis of config file.")
                                                                            # 生成数据库子程序
    parser_gendata.add_argument("filename", help='The name of the config file (in the ./config/ direction.)')
    cmd_args = cmd_parser.parse_args()

    if cmd_args.sub_cmd == "test":
        tester = PyGDB("project_example.yml")
        print("测试!")
        tester.release_project()
    elif cmd_args.sub_cmd == "gendata":
        """
        生成数据库
            1. 读取配置文件
            2. 检查是否已经生成过 -> 退出
            3. 对所有的源代码进行编译
            4. 跑测试用例并填写数据库表
        """
        if not cmd_args.filename:
            PyGdbUtil.log(2, '请指定配置文件')

        # 1. 读取配置文件
        PyGdbUtil.log(0, '正在读取配置文件')
        pg = None
        try:
            pg = PyGDB(cmd_args.filename)
            pg.db.init_project(pg.conf.pro_name, pg.conf.pro_table_prefix)
            pg.print_project_info()
        except IOError as io_error:
            if io_error.errno == 2:
                PyGdbUtil.log(2, '找不到配置文件: ' + cmd_args.filename)
            else:
                PyGdbUtil.log(2, '配置文件打开异常: \n' + io_error.message)

        # 2. 检查是否已经生成过 -> 退出
        exist_project = not pg.db.new_project()
        if exist_project:
            print '已经处理过该程序, 任务中止'
            exit(0)

        # 3. 对所有的源代码进行编译, 检查每一个文件是否编译成功
        all_compile_ok = True
        for source_file in pg.conf.pro_source_list:
            PyGdbUtil.compile(source_file, '-O0 -g -o ' + source_file + '.p')
            if not PyGdbUtil.exist_file(source_file + '.p'):
                PyGdbUtil.log(1, '失败: ' + source_file)
                all_compile_ok = False

        if not all_compile_ok:
            PyGdbUtil.log(2, '没有完全编译成功, 任务中止')



    print "显示内容: " + cmd_args.sub_cmd + "  <----"
else:
    raise Exception("This program isn't a module.")
