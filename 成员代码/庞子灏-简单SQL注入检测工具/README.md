# 你的姓名 - 简单SQL注入检测工具

**功能说明**：
- 这是一个简单的 SQL 注入漏洞检测脚本
- 支持对 GET/POST 参数进行基础注入测试
- 使用 Python + requests 库实现
- 可检测常见报错型注入点

**使用方法**：
```bash
python sql_inject.py -u "http://target.com/login.php" -p "username"
```

**测试环境**：
- Python 3.x
- 需要安装 `requests`：`pip install requests`

**实现原理**：
通过构造常见 SQL 注入 payload（如 ' OR '1'='1），观察返回页面差异来判断是否存在注入漏洞。

**注意**：仅用于合法授权的安全测试与学习，请勿用于非法用途。
