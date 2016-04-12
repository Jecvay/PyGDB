#coding=utf-8

import shlex
import subprocess
import sys

cmd = shlex.split("gdb")
print cmd
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

while True:
    line = sys.stdin.readline()
    if not line:
        break
    print "写入: " + line + "<<<"

    p.stdin.write(line)
    p.stdin.flush()
    print p.stdout.readline()

print "程序结束"