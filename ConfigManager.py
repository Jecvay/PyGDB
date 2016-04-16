# coding=utf-8

import yaml


class ConfigManager:
    def __init__(self):
        stream = file('config/config.yml', mode='r')
        self.dict = yaml.load(stream)
        self.prodict = None

    def load_project_config(self, filename):
        stream = file('config/' + str(filename), mode='r')
        self.prodict = yaml.load(stream)

if __name__ == '__main__':
    print "测试配置管理器"
    cm = ConfigManager()
    print "总配置: " + str(cm.dict)
    cm.load_project_config('project_example.yml')
    print "项目配置: " + str(cm.prodict)
    print "配置管理器测试完毕"
