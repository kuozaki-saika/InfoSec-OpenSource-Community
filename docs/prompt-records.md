# Prompt 记录

工具：Claude Code（Anthropic）

---

## 第1轮：需求理解与选题

**用户 Prompt：**
> 看看pdf，仓库是https://github.com/kuozakisaika2004-stack/InfoSec-OpenSource-Community，怎么完成

**AI 行为：**
- 读取 PDF（作业三要求）
- 拉取仓库结构（README, 成员代码, 漏洞靶场）
- 分析林翔个人代码（随机森林文档去噪）
- 识别仓库缺失 `docs/` 和 `reports/` 目录

**AI 回复关键片段：**
> 选题建议：把现有的 denoise_document.py 包装成 Flask Web API，增加文件类型白名单校验、文件大小限制、上传频率限制、路径遍历防护。这是最自然的方向——原有代码 + 安全加固。

---

## 第2轮：制定计划

**用户 Prompt：**
> 随便，作业罢了

**AI 行为：**
- 生成完整实施计划，包含 5 步工作流程
- 列出 8 个文件的变更清单
- 进入计划审批流程

**安全约束表达方式：**
在 Prompt 中通过计划文件明确列出安全要求：
- 文件类型白名单（只允许常见图片格式）
- 文件大小上限 16MB
- 路径遍历防护（文件名清理）
- 错误时不泄露内部路径
- 频率限制

---

## 第3轮：代码生成（安全约束生效）

**用户上下文（来源于 constraint-doc.md + 计划中的安全要求）：**
Claude Code 根据已建立的安全约束，生成 `api_server.py`。

**AI 生成的代码安全关键片段：**

```python
# 扩展名白名单（约束1：文件类型校验）
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif'}

# 大小限制（约束2：16MB）
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 频率限制（约束3：DoS防护）
def check_rate(ip):
    """频率限制检查，超限返回 True"""
    now = datetime.now()
    rate_log[ip] = [t for t in rate_log[ip] if now - t < RATE_WINDOW]
    if len(rate_log[ip]) >= RATE_LIMIT:
        return True
    rate_log[ip].append(now)
    return False

# 文件名清理（约束4：路径穿越防护）
safe_name = secure_filename(file.filename)
unique_name = f"{uuid.uuid4().hex}_{safe_name}"

# 统一错误响应（约束5：不泄露内部信息）
except Exception:
    return jsonify({"error": "服务内部错误"}), 500
```

> 安全约束全部落实在代码逻辑中，无"仅注释声明"的情况。

---

## 第4轮：文档生成

**用户 Prompt（隐含）：**
按 PDF 的 4 步流程生成所有安全管理文档。

**AI 生成文件清单：**
- `docs/risk-analysis.md` — 6项风险识别
- `docs/constraint-doc.md` — AI对话约束粘贴模板
- `docs/security-checklist.md` — 安全审查清单
- `docs/fix-report.md` — 整改说明与验证
- `docs/review-record.md` — 两层审查记录
- `reports/before-after-diff.md` — 改造前后对比
- `reports/scan-report.md` — 安全扫描报告

---

## 关键交互截图说明

| 环节 | 截图内容 | 对应文件 |
|------|----------|----------|
| 需求分析 | PDF提取 + 仓库分析 | 第1轮 |
| 计划制定 | 计划文件内容 | 第2轮 |
| 代码生成 | api_server.py 安全关键代码 | 第3轮 |
| 审查记录 | 两层审查结果 | review-record.md |

截图已单独保存提交至云平台。
