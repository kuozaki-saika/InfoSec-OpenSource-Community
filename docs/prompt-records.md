# Prompt 记录

## Prompt 1：需求分析

**用户输入：**
> 看看pdf，仓库是https://github.com/kuozakisaika2004-stack/InfoSec-OpenSource-Community，怎么完成

**AI 回复摘要：**
识别作业要求（4步安全管理流程），分析仓库现状，提出选题建议（Flask API + 安全加固）。

## Prompt 2：编写 API 代码 + 约束

**用户输入（隐含约束从 constraint-doc.md）：**
> 给去噪系统加 Flask API，安全要求：文件类型白名单、大小限制、路径穿越防护、频率限制、错误不泄露路径

**AI 生成代码文件：**
`api_server.py` — 包含所有安全约束的完整实现。

## Prompt 3：生成安全文档

**用户输入：**
> 生成 docs/ 下 risk-analysis.md, constraint-doc.md, security-checklist.md, fix-report.md

**AI 回复摘要：**
依次生成所有安全管理过程文档。

## 安全约束传递方式

每次新对话或新任务时，先粘贴 `constraint-doc.md` 内容，确保 AI 记住安全约束。
