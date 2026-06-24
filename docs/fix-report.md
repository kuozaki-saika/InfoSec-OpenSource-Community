# 整改说明与验证记录

## 第一步：风险识别

> 详见 `docs/risk-analysis.md`

识别出 6 项安全风险：任意文件上传、路径穿越、DoS(大文件)、DoS(高频)、信息泄露、恶意图像。

## 第二步：安全约束表达

> 详见 `docs/constraint-doc.md`、`docs/prompt-records.md`

将风险转化为 5 项硬约束写入 AI Prompt，每次对话前粘贴 `constraint-doc.md`。

## 第三步：AI生成结果检查

> 详见 `docs/review-record.md`

- **第一层（对照Prompt）**：5项安全约束全部在代码逻辑中落地，无"仅注释声明"情况
- **第二层（人工）**：认证授权、最小权限、错误响应均通过审查，无业务逻辑缺陷

审查发现的问题：**无**。AI生成代码满足全部安全约束，初审即通过。

## 第四步：整改、验证与过程留痕

### 原始代码的安全问题（已存在）

| # | 问题 | 严重程度 |
|---|------|----------|
| 1 | 原 `denoise_document.py` 无任何输入校验 | 高 |
| 2 | 原代码使用 `os.path.join` 直接拼接路径，无穿越防护 | 中 |
| 3 | 原代码异常时 crash，暴露完整堆栈信息 | 低 |

### 整改措施

| 问题 | 怎么改 | 改完应满足什么条件 |
|------|--------|-------------------|
| 无输入校验 | API层加扩展名白名单 + MIME二次校验 | 非法文件被拒绝（400） |
| 路径穿越 | `secure_filename()` + UUID 前缀重命名 | 文件名不再参与路径拼接 |
| 错误暴露 | `try/except` + 统一 JSON 错误格式 | 任何异常不暴露路径/堆栈 |

### 验证记录

| 测试用例 | 命令 | 预期 | 结果 |
|----------|------|------|------|
| 正常图片 | `curl -F "file=@test.png" localhost:5000/denoise` | 200 | 通过 |
| PHP文件 | `curl -F "file=@shell.php" localhost:5000/denoise` | 400 | 通过 |
| 路径穿越 | `curl -F "file=@../../etc/passwd" localhost:5000/denoise` | 安全转义 | 通过 |
| 超大文件 | `curl -F "file=@20mb.bin" localhost:5000/denoise` | 413 | 通过 |
| 损坏图片 | `curl -F "file=@corrupt.png" localhost:5000/denoise` | 422 | 通过 |
| 高频请求 | 连续 25 次请求 | 第21+次返回429 | 通过 |

### 验证结论

全部 6 项验证通过。原 3 个安全问题已消除，未引入新安全隐患。

> 详见 `reports/scan-report.md`、`reports/before-after-diff.md`
