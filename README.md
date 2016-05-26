# PyGDB
Python 调用 GDB 的一个很方便使用的东东
- 支持远程数据库
- 方便的配置管理


## 使用说明
- 配置公共配置文件 ./config/config.yml 本配置只需要设置一次, 多个项目共享使用
- 测试数据库连接 ./pygdb.py test
- 配置项目配置文件 ./config/project.yml 其中 project.yml 文件名自选, 具体配置可以参考 project_example.yml
- 执行项目数据生成程序 ./pygdb.py gendata project.yml 其中 project.yml 为 ./config/ 目录下的项目配置文件


## 工作流

### 1. 产生项目数据
- 检查 **c程序** 以及对应的 **源代码** 是否准备就绪 (yaml配置文件)
- 扫描源代码, 获取断点信息, 存入数据库
- 运行 gdb, 获取所需数据, 存入数据库

### 2. 使用项目数据
- 读取数据库, 产生基本信息
- 封装 API, 对数据库数据进行组合, 处理, 并返回
- 在封装 API 的基础上进行 Restful API 开发


## 第三方库
- [pymysql] Python MySQL: https://github.com/PyMySQL/PyMySQL 安装: pip install pymysql
- [pyYaml] Python Yaml: http://pyyaml.org/ 安装: pip install pyyaml


## 文件说明
- PyGDB.py 主程序
- PyGdbDb.py 数据库管理器
- ConfigManager.py 配置文件管理器

## 数据库说明

(其中 ProjectPrefix_ 为表前缀, 在项目配置文件中定义)

1. ProjectPrefix_BreakPoint 断点表
    - pid 程序id
    - bid 断点id
    - lineNumber    行号
    - funcName      函数名称
    - funcList      从程序执行到当前断点的函数列表
1. ProjectPrefix_PStackSize 每个程序&每个测试用例的组合下, 最坏栈大小 以及 是否执行成功
    - pid           程序id
    - tid           测试用例id
    - stackSize     最坏栈大小
    - pass          是否执行成功
1. ProjectPrefix_FStackSize 每个程序&每个测试用例&每个函数  使用的最大栈大小 (*)
    - pid
    - tid
    - fid
    - stackSize
1. ProjectPrefix_FrameVariable 某一帧下, 某变量的信息(断点处帧信息)
    - bid           断点
    - varName       变量名
    - varValue      变量值
    - varSize       变量占用内存大小
1. ProjectPrefix_FuncAdjacencyList 函数邻接表
    - pid
    - tid           pid & tid 限定出一个邻接表
    - parFid        父亲函数id
    - fid           函数id
1. ProjectPrefix_Function       函数列表
    - fid           函数id
    - funcName      函数名
1. ProjectPrefix_TestCase       测试用例列表
    - tid
    - testStr



## GDB 说明

断点需要获取的信息:
- 当前栈大小
- 函数调用序列
- 栈帧信息
    - 变量 名/值
    - 大小信息

### 栈帧说明
- 计算栈帧通常使用的方法: GCC 编译的时候加上 -O0 参数使得编译器关闭优化, EBP(RBP)寄存器能表示出栈帧的栈底指针, 然后使用 $EBP - $ESP 获取栈帧大小.
- 但是栈帧大小不包括函数调用的时候实参占用的空间.
- GDB 刚好为我们保存了 ESP 的上一个位置的值. 因此使用上一个位置的值减去当前位置的值似乎可以得到包含了实参占用空间与栈帧占用空间的和(我称为扩展栈帧大小). 但是这要求CPU架构没有对内存地址进行随机化处理.
- 而 i686 架构可以避免 CPU 启用内存地址随机化的特性. 可以使用如下命令使用 i686 架构启动
    - GDB setarch i686 -R gdb ProgramName

### 邻接表说明
- 当GDB停在断点时, 函数栈顶元素A以及栈次顶(大雾)元素B的关系是 B调用了A, 此时应该增加 B->A 的边权.

##版本说明

GDB 7.11


1. 安装编译环境
sudo apt-get install build-essentials

2. 安装python第三方库
sudo pip install yaml
sudo pip install pymysql

3. 安装数据库
sudo apt-get install mysql-server

4. 建立数据库
启动:  mysql -uroot -p
命令:  create database pygdb;

5. 在 config 文件夹下创建工程配置.

6. python PyGDB.py gendata project_example.yml

