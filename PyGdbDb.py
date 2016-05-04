# coding=utf-8
import pymysql
import PyGdbUtil

class PyGdbDb:
    # 初始化: 连接数据库
    def __init__(self, host, port, dbname, user, passwd):
        self.project = None
        self.table_prefix = None
        try:
            self.connection = pymysql.connect(
                host=host, port=int(port), user=user, password=passwd, db=dbname, charset="utf8mb4")
            self.cursor = self.connection.cursor()
        except Exception as e_con:
            print '数据库连接错误, 程序中止'
            print e_con
            exit(-1)

    def test(self):
        print '正在测试数据库连接'
        print '数据库连接: ' + str(self.connection.get_host_info()) if self.connection else '数据库连接异常'
        print '数据库游标: ' + str(self.cursor) if self.cursor else '数据库游标异常'
        print '数据库连接测试完毕'

        print '检查表 aabb 是否存在'
        if self.exist_table('aabb'):
            print '存在'
        else:
            print '不存在'

        print '初始化项目 example'
        self.init_project('example', 'example_')
        self.new_project()
        PyGdbUtil.log(0, '初始化完毕')

    # 初始化项目
    def init_project(self, project_name, table_prefix):
        self.project = project_name
        self.table_prefix = table_prefix

    # 检测是否存在该项目 不存在->创建 返回True; 存在->返回 False
    def new_project(self):
        if not self.table_prefix:
            PyGdbUtil.log(2, '未指定数据库前缀')
        exist_project = self.exist_table(self.table_prefix + 'BreakPoint')

        # 创建数据库表
        if not exist_project:
            self.create_table(self.table_prefix + "BreakPoint(pid INT, lineNumber INT, funcName TEXT, funcList TEXT)")
            self.create_table(self.table_prefix + "PStackSize(pid INT, tid INT, stackSize INT, pass TINYINT)")
            self.create_table(self.table_prefix + "FStackSize(pid INT, tid INT, fid INT, stackSize INT)")
            self.create_table(self.table_prefix + "FrameVariable(varName CHAR, varValue TEXT, varSize INT)")
            self.create_table(self.table_prefix + "FuncAdjacencyList(parFid INT, fid INT)")
            self.create_table(self.table_prefix + "Function(fid INT, funcName CHAR)")
            self.create_table(self.table_prefix + "TestCase(tid INT AUTO_INCREMENT primary key, testStr TEXT)")
            self.commit()
            return True
        else:
            return False

    # 插入测试用例
    def insert_test_case(self, test_str):
        self.execute("insert into " + self.table_prefix + "TestCase(testStr) VALUES('%s')" % test_str)

    # 插入程序断点
    def insert_breakpoint(self, pid, line_number, func_name):
        return # 测试
        PyGdbUtil.log(0, str(pid) + " " + str(line_number) + " " + str(func_name))
        self.execute("insert into " + self.table_prefix +
                     "BreakPoint(pid, lineNumber, funcName) VALUES (%s, %s, '%s')" % (pid, line_number, func_name))

    # 数据库中插入断点
    def info_breakpoint_handler(self, pid, gdb_info_breakpoint):
        ss = gdb_info_breakpoint.split("\n")
        for s in ss:
            if 0 < s.find("breakpoint     keep y"):
                s2 = s.split()
                s3 = s2[8].split(":")
                self.insert_breakpoint(pid, s3[1], s2[6])
                # self.execute("insert into breakpoint values (%s, '%s', '%s', %s)" % (s2[0], s2[6], s3[0], s3[1]))

    # 检查是否存在一张表
    def exist_table(self, table_name):
        try:
            self.execute('select * from ' + table_name)
            return True
        except Exception:
            return False

    # 创建表
    def create_table(self, table_list):
        try:
            PyGdbUtil.log(0, "创建表" + table_list)
            self.execute("create table if not exists " + table_list)
        except Exception as e:
            # print e
            PyGdbUtil.log(2, "创建表" + table_list + "失败! 请检查数据表前缀是否有非法字符.")

    # 获取测试样例
    def get_test_case_by_tid(self, tid):
        self.execute("SELECT testStr FROM " + self.table_prefix + "TestCase WHERE tid='%s'" % tid)
        return self.cursor.fetchone()[0]

    # 获取测试样例总数
    def get_test_case_cnt(self):
        self.execute('SELECT max(tid) FROM ' + self.table_prefix + 'TestCase')
        return int(self.cursor.fetchone()[0])

    # 获取指定程序的断点列表
    def get_breakpoint_list(self, pid):
        self.execute('SELECT lineNumber FROM ' + self.table_prefix + 'BreakPoint WHERE pid="%s"' % pid)
        all = self.cursor.fetchall()
        return [x[0] for x in all]

    # 执行 sql 语句
    def execute(self, sql_cmd):
        return self.cursor.execute(sql_cmd)

    # commit 操作
    def commit(self):
        self.connection.commit()

    """
        ==================================================================
            下方是 RestFul API 直接需要用到的 api
            我擦, 这个好像应该放到另一个工程里面 - -#
        ==================================================================
    """

    # getWorstStackSize(String program String  t1){} input1+program  getWorstStackSize(){}
    # tid + pid --> Worst Stack Size
    def api_worst_stack_size(self, pid, tid):
        pass

    def api_max_stack_size(self, pid, tid, fid):
        pass

    # 给出正确程序的pid 以及比较程序的 pid, 以及测试用例集合(tid列表), 返回程序执行成功与否的TF表
    def api_result(self, correct_pid, test_pid, tid_list):
        pass

    # 返回程序断点列表
    def api_breakpoint_list(self, pid, tid):
        pass

    # 断点处函数栈列表
    def api_breakpoint_func_list(self, pid, breakpoint):
        pass

    # 断点处栈帧信息
    def api_breakpoint_frame_info(self, pid, breakpoint):
        pass

    # 返回函数调用图的邻接表
    def api_function_graph(self, pid, tid):
        pass

    # 返回函数列表
    def api_function_list(self, pid):
        pass



if __name__ == '__main__':
    print "PyGDB Database 测试模式"
    try:
        dbc = PyGdbDb('127.0.0.1', '3306', 'pygdb', 'root', 'Sbdljw1992')
        print '数据库连接成功'
        dbc.test()
        dbc.connection.close()
        print '数据库连接断开成功'
    except Exception as e:
        print '严重错误: ' + str(e)
        exit(-1)
