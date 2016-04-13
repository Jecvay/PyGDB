# PyGDB
Python 调用 GDB 的一个很方便使用的东东

## 工作流

### 1. 产生项目数据
- 检查 **c程序** 以及对应的 **源代码** 是否准备就绪 (yaml配置文件)
- 扫描源代码, 获取断点信息, 存入数据库
- 运行 gdb, 获取所需数据, 存入数据库

### 2. 使用项目数据
- 读取数据库, 产生基本信息
- 封装 API, 对数据库数据进行组合, 处理, 并返回
- 在封装 API 的基础上进行 Restful API 开发
