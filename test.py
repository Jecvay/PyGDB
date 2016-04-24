#coding=utf-8

import sys

from gdblib.StateGDB import *

x = StateGDB("/home/jecvay/fantastic/c/totinfo/v1/tot_info.c.p")

print x.question("b 55")
print x.question("r")
print x.state()
