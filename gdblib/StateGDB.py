# coding=utf-8

"""
    对 GDB 模块输出的信息进行更高层的封装
"""

import re
import GDB
import string
from TimedMessage import TimedMessage

# GDB interface with special state fetching capability
class StateGDB(GDB.GDB):
    CHAR_PATTERN    = re.compile("(?P<value>\d+) +(?P<character>'.*')")
    STRING_PATTERN  = re.compile('(?P<pointer>0x[^ ]+) +(?P<string>".*")')
    POINTER_PATTERN = re.compile(".*(?P<value>0x[0-9a-f]+)")
    FUNCTION_POINTER_PATTERN = re.compile(".*(?P<value>0x[0-9a-f]+) <(?P<identifier>[^>]*)>")

    def _unfold_pointer(self, name, frame, value, vars):
        if string.find(value, "(void *)") >= 0:
            return                  # Generic pointer - ignore

        if value == "0x0":
            vars[(name, frame)] = "0x0" # NULL pointer
            return

        deref_value = self.question("output *(" + name + ")")

        if deref_value[:2] == '{\n':
            # We have a pointer structure.  Dereference elements.
            SEP = " = "
            for line in string.split(deref_value, "\n"):
                separator = string.find(line, SEP)
                if separator < 0:
                    continue

                member_name = name + "->" + line[0:separator]
                member_value = line[separator + len(SEP):]

                self._fetch_values(member_name, frame, member_value, vars)

            return

        if deref_value[0] == '{':
            # Some function pointer.  Leave it unchanged.
            return

        # Otherwise, assume it's an array or object on the heap
        # (hopefully)

        if name == "argv":
            # Special handling for program arguments.
            elems = 4096
        else:
            # This trick will get the number of elements (if we use
            # GNU malloc on Linux)
            elems = self.question("output (((int *)(" + name +
                                "))[-1] & ~0x1) /" +
                                "sizeof(*(" + name + "))")
            #print("###########"+elems)
            if len(elems)<=20:
                elems = string.atoi(elems)
            else:
                return

        if elems > 10000:
            return                      # Cannot handle this

        beyond = 1                      # Look 1 elements beyond bounds

        for i in range(0, elems + beyond):
            elem_name = name + "[" + `i` + "]"
            elem_value = self.question("output " + elem_name)

            self._fetch_values(elem_name, frame, elem_value, vars)
            if name == "argv" and elem_value == "0x0":
                break               # Stop it


    # Fetch a value NAME = VALUE from GDB into VARS, with special
    # handling of pointer structures.
    def _fetch_values(self, name, frame, value, vars):
        value = string.strip(value)
        value = string.replace(value, "\n", "")

        # print "Handling " + name + " = " + value

        # GDB reports characters as VALUE 'CHARACTER'.  Prefer CHARACTER.
        m = self.CHAR_PATTERN.match(value)
        if m is not None:
            vars[(name, frame)] = m.group('character')
            return

        # GDB reports strings as POINTER "STRING".  Prefer STRING.
        m = self.STRING_PATTERN.match(value)
        if m is not None:
            vars[(name, frame)] = m.group('string')
            return

        # GDB reports function pointers as POINTER <IDENTIFIER>.
        # Prefer IDENTIFIER.
        m = self.FUNCTION_POINTER_PATTERN.match(value)
        if m is not None:
            vars[(name, frame)] = m.group('identifier')
            return

        # In case of pointers, unfold the given data structure
        if self.POINTER_PATTERN.match(value):
            self._unfold_pointer(name, frame, value, vars)
            return

        # Anything else: Just store the value
        vars[(name, frame)] = value


    # Store mapping (variable, frame) => values in VARS
    def _fetch_variables(self, frame, vars):
        SEP = " = "
        IDENTIFIER = re.compile("[a-zA-Z_]")
#        print "-----------------"
#        print self.question("info variables")
#        print "-----------------"
        for query in ["info locals", "info args"]:
            list = self.question(query)
            lines = string.split(list, "\n")

            # Some values as reported by GDB are split across several lines
            for i in range(1, len(lines)):
                if lines[i] != "" and not IDENTIFIER.match(lines[i][0]):
                    lines[i - 1] = lines[i - 1] + string.strip(lines[i])

            for line in lines:
                separator = string.find(line, SEP)
                if separator > 0:
                    name  = line[0:separator]
                    value = line[separator + len(SEP):]
                    self._fetch_values(name, frame, value, vars)

        return vars


    # Return mapping (variable, frame) => values
    def state(self):
        t = TimedMessage("Capturing state")
        vars = {}
        frame = 0

        reply = "#0"
        while string.find(reply, "#") != -1:
            reply = self.question("down")

        reply = "#0"
        while string.find(reply, "#") != -1:
            self._fetch_variables(frame, vars)
            reply = self.question("up")
            frame = frame + 1

        t.outcome = `len(vars.keys())` + " variables"
        return vars

    """
        By Jecvay
        必须停在断点的时候调用本方法

        断点需要获取的信息:
            - 当前栈大小
            - 函数调用序列
            - 栈帧信息
                - 变量 名/值
                - 大小信息

        计算栈帧通常使用的方法: GCC 编译的时候加上 -O0 参数使得编译器关闭优化, EBP(RBP)寄存器能
        表示出栈帧的栈底指针, 然后使用 $EBP - $ESP 获取栈帧大小.

        但是栈帧大小不包括函数调用的时候实参占用的空间.

        GDB 刚好为我们保存了 ESP 的上一个位置的值. 因此使用上一个位置的值减去当前位置的值似乎可以得
        到包含了实参占用空间与栈帧占用空间的和(我称为扩展栈帧大小). 但是这要求CPU架构没有对内存地址进
        行随机化处理.

        而 i686 架构可以避免 CPU 启用内存地址随机化的特性. 可以使用如下命令使用 i686 架构启动 GDB
            setarch i686 -R gdb ProgramName
    """
    def get_breakpoint_info(self):
        info = {
            "stack_size": None,
            "func_list": "",
            "frame": {
                "frame_size": -1,
                "var_list": [],
                "var_value": [],
                "var_size": []
            }
        }

        # 获取函数栈列表
        info['func_list'] = self.question("backtrace")

        # 获取当前栈帧大小
        info['frame']['frame_size'] = self.__frame_expend_size()

        # 获取当前变量列表以及变量值
        output = (self.question("info args") + self.question('info local')).split('\n')
        for line in output:
            var_split = line.split(' ')
            var_name = var_split[0]
            if var_name == '':
                continue
            var_value = ''.join(var_split[2:])

            info['frame']['var_list'].append(var_name)
            info['frame']['var_value'].append(var_value)

        # 获取变量大小
        for var in info['frame']['var_list']:
            output = self.question('p sizeof(' + var + ')').split(' ')[2]
            info['frame']['var_size'] = int(output)

        # 获取栈大小
        reply = "#0"
        while string.find(reply, "#") != -1:
            reply = self.question("down")

        reply = "#0"
        stack_size = 0
        while string.find(reply, "#") != -1:
            stack_size += self.__frame_expend_size()
            reply = self.question("up")

        info['stack_size'] = stack_size

        return info

    """
        By Jecvay
        私有方法: 计算当前帧的 扩展栈帧 大小
    """
    def __frame_expend_size(self):
        # 获取栈帧信息

        frame_info = str(self.question('i f'))
        frame_size = str(self.question("p $ebp-$esp")).split(" ")[2]  # 寄存器 EBP - ESP 得到栈帧大小(不含实参)
        arg_list = self.question("info args")

        # 获取上一个 $sp 值
        PRE_SP_MODEL = "Previous frame's sp is "
        pre_sp_str_offset_start = frame_info.find(PRE_SP_MODEL) + len(PRE_SP_MODEL)
        pre_sp_str_offset_end = frame_info.find('\n', pre_sp_str_offset_start)
        pre_sp_str = frame_info[pre_sp_str_offset_start:pre_sp_str_offset_end]
        pre_sp_int = int(pre_sp_str, 16)

        # 获取当前 $sp 值
        sp_str = ""
        if len(pre_sp_str) > 10:  # 64位机
            sp_str = str(self.question("p/x $rsp")).split(" ")[2]
        else:
            print "致命错误: 32位机器上运行"
            exit()
        sp_int = int(sp_str, 16)

        # 计算扩展栈帧大小
        frame_expend_size = pre_sp_int - sp_int

        return frame_expend_size

    # Return (opaque) list of deltas
    def deltas(self, state_1, state_2):
        deltas = []
        for var in state_1.keys():
            value_1 = state_1[var]
            if not state_2.has_key(var):
                continue                # Uncomparable

            value_1 = state_1[var]
            value_2 = state_2[var]
            if value_1 != value_2:
                deltas.append((var, value_1, value_2))

        deltas.sort()
        return deltas


    # Apply (opaque) list of deltas to STATE_1
    def apply_deltas(self, deltas):
        cmds = self.delta_cmds(deltas)
        for cmd in cmds:
            self.question(cmd)

    def delta_cmds(self, deltas):
        cmds = []
        current_frame = None
        for delta in deltas:
            (var, value_1, value_2) = delta
            (name, frame) = var
            if frame != current_frame:
                cmds.append("frame " + `frame`)
                current_frame = frame

            cmds.append("set variable " + name + " = " + value_2)

        return cmds