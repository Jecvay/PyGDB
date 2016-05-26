# coding=utf-8

import argparse
import PyGdbUtil
from PyGdbDb import PyGdbDb
from ConfigManager import ConfigManager
from gdblib import StateGDB

import re


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
            pg.db.clear_project()
            pg.db.new_project()
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
            # break       # 调试开关 -> 跳过插入测试用例部分
            fp = open(file_path, 'r')
            test_str = ""
            for line in fp:
                test_str += line
            fp.close()
            pg.db.insert_test_case(test_str)
        pg.db.commit()

        # 5. 代码断点写入数据库 & 获取断点函数列表
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

            function_list = pg.db.get_function_list(output)
            pg.db.insert_function_list(function_list)

            pg.db.info_breakpoint_handler(pid, output)

            pg.db.commit()
            # print output
            gdb.cleanup()
            # PyGdbDb.insert_breakpoint(pid, line_number, func_name)
            # 以下一行为测试用, 减少测试程序.
            break


        # 6. 调试程序   外层循环: 程序; 内层循环: 测试样例

        test_cnt = pg.db.get_test_case_cnt()
        program_cnt = len(pg.conf.pro_source_list)
        PyGdbUtil.log(0, "--------------------------")
        PyGdbUtil.log(0, "    GDB 调试开始")
        PyGdbUtil.log(0, "测试样例总数: " + str(test_cnt))
        PyGdbUtil.log(0, "程序总数: " + str(program_cnt))
        PyGdbUtil.log(0, "循环总数: " + str(test_cnt * program_cnt))
        PyGdbUtil.log(0, "--------------------------")

        pid = 0
        func_name_pattern = re.compile(r' ([^ ]*) \(')      # 用于找出函数调用关系
        for file_path in pg.conf.pro_source_list:
            pid += 1
            for tid in xrange(1, test_cnt + 1):
                # 打开程序
                gdb = StateGDB.StateGDB(file_path + '.p')

                # 插入断点
                breakpoint_list = pg.db.get_breakpoint_list(pid)
                for bp in breakpoint_list:
                    gdb.question("b " + str(bp))

                print gdb.question("info b")

                x = pg.db.get_test_case_by_tid(1)
                output = gdb.question(["run \n" + x + "\n"])
                print "output: " + output

                # 处理每一个断点!!!
                max_stack_size = -1
                while output.find("\nBreakpoint ") >= 0:
                    bid = int(output[output.find("\nBreakpoint ") + len('\nBreakpoint '):].split(' ')[0][:-1])
                    state = gdb.get_breakpoint_info()
                    bid += 1
                    s = output
                    # print "GDB输出: " + s + "\n-----------\n"
                    print "断点信息: " + str(state) + "\n=========\n\n"

                    # 信息存入数据库
                    for i in xrange(0, len(state['frame']['var_list'])):
                        var_name = state['frame']['var_list'][i]
                        var_value = state['frame']['var_value'][i]
                        var_size = state['frame']['var_size'][i]
                        pg.db.insert_frame_var(bid, var_name, var_value, var_size)

                    fid = int(pg.db.get_fid_by_bid(bid))
                    pg.db.insert_frame_stack_size(pid, tid, fid, state['stack_size'])
                    max_stack_size = max(max_stack_size, state['stack_size'])
                    func_list_info = gdb.question('info stack')
                    func_list = func_name_pattern.findall(func_list_info)
                    pg.db.insert_edge(pid, tid, func_list[1], func_list[1])

                    try:
                        output = gdb.question("c", timeout=1)       # 超时: 给每个测试用例的最长计算时间
                    except Exception as e:
                        PyGdbUtil.log(1, "等待程序超时, 结束调试")
                        break
                pg.db.insert_max_stack_size(pid, tid, max_stack_size)
                pg.db.commit()
                gdb.cleanup()




        # 结束, 释放资源
        pg.release_project()



    print "显示内容: " + cmd_args.sub_cmd + "  <----"
else:
    raise Exception("This program isn't a module.")
