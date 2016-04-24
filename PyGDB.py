# coding=utf-8

import argparse
import PyGdbUtil
from PyGdbDb import PyGdbDb
from ConfigManager import ConfigManager
from gdblib import StateGDB


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
            # exit(0)

        # 3. 对所有的源代码进行编译, 检查每一个文件是否编译成功
        all_compile_ok = True
        failed_list = []
        for source_file in pg.conf.pro_source_list:
            break       # 调试开关 -> 跳过编译部分
            if PyGdbUtil.compile(source_file, pg.conf.pro_gcc_args + ' -O0 -g -o ' + source_file + '.p'):
                failed_list.append(source_file)
                all_compile_ok = False

        if not all_compile_ok:
            print "--------------- 编译完毕, 失败列表如下------------"
            for line in failed_list:
                print line
            PyGdbUtil.log(2, '没有完全编译成功, 任务中止')
        else:
            print '恭喜! 所有程序编译成功!'

        # 4. 测试用例写入数据库
        for file_path in pg.conf.pro_test_list:
            fp = open(file_path, 'r')
            test_str = ""
            for line in fp:
                test_str += line
            fp.close()
            pg.db.insert_test_case(test_str)
        pg.db.commit()

        # 5. 代码断点写入数据库
        pid = 0
        for file_path in pg.conf.pro_source_list:
            gdb = StateGDB.StateGDB(file_path + '.p')
            pid += 1
            fp = open(file_path, 'r')
            line_cnt = 0
            for line in fp:
                line_cnt += 1
                if 0 < line.find("return") or 0 < line.find("exit("):
                    output = gdb.question("b " + '%d' % line_cnt)
            fp.close()
            output = gdb.question("info b")
            pg.db.info_breakpoint_handler(pid, output)
            pg.db.commit()
            # print output
            gdb.cleanup()
            # PyGdbDb.insert_breakpoint(pid, line_number, func_name)


        # 6. 调试程序



        # 结束, 释放资源
        pg.release_project()



    print "显示内容: " + cmd_args.sub_cmd + "  <----"
else:
    raise Exception("This program isn't a module.")
