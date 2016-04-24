# coding=utf-8

import yaml


class ConfigManager:
    # 打开全局配置文件, 并解析成dict类型的 self.dict
    def __init__(self):
        stream = file('config/config.yml', mode='r')
        self.dict = yaml.load(stream)
        self.pro_dict = None
        self.pro_name = None
        self.pro_table_prefix = None

    # 打开项目配置文件, 解析成dict类型的 self.pro_dict
    def load_project_config(self, filename):
        stream = file('config/' + str(filename), mode='r')      # 如果打不开文件由上层 handle
        self.pro_dict = yaml.load(stream)
        self.pro_name = self.pro_dict['project']
        self.pro_table_prefix = self.pro_dict['table-prefix']
        self.pro_source_list = self.pro_dict['source-codes']
        self.pro_test_list = self.pro_dict['test-files']
        self.pro_gcc_args = self.pro_dict['gcc-args']

if __name__ == '__main__':
    print "测试配置管理器"
    cm = ConfigManager()

    print "总配置: " + str(cm.dict)
    cm.load_project_config('project_example.yml')

    print "项目配置: " + "\n" + cm.pro_name + "\n" + cm.pro_table_prefix + "\n" + \
        str(cm.pro_source_list) + "\n" + str(cm.pro_test_list)

    print "配置管理器测试完毕"
