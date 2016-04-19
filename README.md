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
1. ProjectPrefix_FrameVariable 某一帧下, 某变量的信息
    - varName       变量名
    - varValue      变量值
    - varSize       变量占用内存大小
1. ProjectPrefix_FuncAdjacencyList 函数邻接表
    - parFid        父亲函数id
    - fid           函数id
1. ProjectPrefix_Function       函数列表
    - fid           函数id
    - funcName      函数名