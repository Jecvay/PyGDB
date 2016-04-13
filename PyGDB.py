# coding=utf-8

import argparse

if __name__ == "__main__":
    # 配置命令行
    cmd_parser = argparse.ArgumentParser(description="Python-GDB Test Suite")
    cmd_sub_parser = cmd_parser.add_subparsers(title="sub command", dest="sub_cmd")
    parser_test = cmd_sub_parser.add_parser('test', description="haha")
    parser_gendata = cmd_sub_parser.add_parser('gendata', description="Generate data in the basis of config file.")
    parser_gendata.add_argument("filename", help='The name of the config file (in the ./config/ direction.)')
    cmd_args = cmd_parser.parse_args()
    if cmd_args.sub_cmd == "test":
        print("测试!")
    elif cmd_args.sub_cmd == "gendata":
        print("生成! " + cmd_args.filename)
    print "显示内容: " + cmd_args.sub_cmd + "  <----"
else:
    raise Exception("This program isn't a module.")
