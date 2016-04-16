# coding=utf-8
import pymysql


class PyGdbDb:
    # 初始化: 连接数据库
    def __init__(self, host, port, dbname, user, passwd):
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
