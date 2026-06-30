# 庞子灏 - 简单SQL注入检测工具

**功能说明**：
- 这是一个简单的 SQL 注入漏洞检测脚本
- 支持对 GET/POST 参数进行基础注入测试
- 使用 Python + requests 库实现

**使用方法**：
```bash
python sql_inject.py -u "http://target.com/login.php" -p "username"
