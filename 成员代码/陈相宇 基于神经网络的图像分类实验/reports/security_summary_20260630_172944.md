# [LOCK] 安全扫描摘要报告

**扫描时间**: 2026-06-30T17:29:44.029861
**扫描耗时**: 0.03 秒
**项目目录**: .

---

## [STATS] 安全评分

| 评分项 | 分数 |
|:---|---|
| **总分** | **80/100** |
| **等级** | **良好 (B)** |

### 评分明细

| 类别 | 扣分/加分 |
|:---|---|
| 危险函数扣分 | -30 |
| 硬编码密钥扣分 | -0 |
| 最佳实践加分 | +10 |
| 依赖漏洞扣分 | -0 |

---

## [WARN] 发现的问题

### 危险函数调用 (14 个)

- `cnn_classifier.py:165` - compile(
- `security\security_scanner.py:40` - exec(
- `security\security_scanner.py:40` - eval(
- `security\security_scanner.py:40` - __import__
- `security\security_scanner.py:40` - compile(
- `security\security_scanner.py:41` - os.system(
- `security\security_scanner.py:41` - os.popen(
- `security\security_scanner.py:41` - subprocess.call(
- `security\security_scanner.py:42` - subprocess.Popen(
- `security\security_scanner.py:42` - subprocess.run(
- `security\security_scanner.py:43` - pickle.load
- `security\security_scanner.py:43` - pickle.loads
- `security\security_scanner.py:44` - yaml.load(
- `security\security_scanner.py:45` - marshal.loads

### 硬编码密钥 (0 个)


### 依赖漏洞 (0 个)



---

## [PASS] 安全最佳实践

| 实践 | 状态 |
|:---|:---:|
| CSRF 防护 | [PASS] 已实现 |
| SQL 注入防护 | [PASS] 已实现 |
| 密码哈希 | [PASS] 已实现 |
| 输入验证 | [PASS] 已实现 |
| 错误处理 | [PASS] 已实现 |
| 速率限制 | [PASS] 已实现 |
| 会话安全 | [PASS] 已实现 |
| 文件上传安全 | [PASS] 已实现 |

---

> 此报告由 SecurityScanner 自动生成
