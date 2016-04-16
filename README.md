# PyGDB
Python 调用 GDB 的一个很方便使用的东东


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
- [pyYaml] Python Yaml: http://pyyaml.org/ 安装: pip intall pyyaml


## 文件说明
- PyGDB.py 主程序
- PyGdbDb.py 数据库管理器
- ConfigManager.py 配置文件管理器