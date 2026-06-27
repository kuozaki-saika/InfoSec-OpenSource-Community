# Prompt 记录 - 权限控制中间件

## 操作人：徐元昊
## 工具：Codex (GPT-5)

---

## Prompt 1：需求分析与风险识别

### 输入
> 作为 Upload-Labs 靶场的权限控制中间件开发者，我需要分析在现有认证系统基础上添加角色权限控制的安全风险。认证系统已有用户注册/登录/登出，使用 Session + JSON 文件存储。我的任务是添加基于角色的访问控制（RBAC），让不同用户看到/访问不同关卡。

### AI 输出要点
- 识别了 12 个安全风险，包括权限提升、越权访问、Session 固定攻击等
- 确定了三层防御策略：认证层 → 权限层 → 业务层
- 明确需要最小权限原则

---

## Prompt 2：权限配置与中间件设计

### 输入
> 根据风险分析结果，设计一个适用于 Upload-Labs 的权限控制中间件，需满足以下约束：
> 1. 定义 `user` 和 `admin` 两个角色
> 2. 普通用户可以访问 Pass-01~Pass-18，高级关卡 Pass-19~Pass-21 仅管理员可访问
> 3. 未登录用户通过 require_login() 拦截，已登录但权限不足返回 403
> 4. 菜单栏根据角色自动显示/隐藏关卡
> 5. 代码风格与现有 upload-labs 一致（PHP 原生，无框架）

### AI 输出要点
- 设计了 `access_config.php`：角色等级常量 + 关卡权限映射表
- 设计了 `access_control.php`：`require_role()`、`check_pass_access()`、`get_accessible_passes()`
- 设计了 `403.php`：友好的权限不足提示页
- 明确中间件与认证系统的接口约定：`$_SESSION['auth_user']`、`find_user()`

---

## Prompt 3：代码集成实现

### 输入
> 将权限控制中间件集成到每个 Pass 的 index.php 中。在每个 Pass 的 include 链中添加 `require_once '../access_control.php'; check_pass_access('Pass-XX');`。同时修改 menu.php，让权限不足的关卡在菜单中以灰色显示并加锁。

### AI 输出要点
- 批量修改了 17 个 Pass 文件（Pass-02~Pass-21，排除无 index.php 的）
- 修改了 menu.php：对 Pass-19/20/21 根据用户角色动态显示
- 修改了 head.php：在右上角显示当前用户的角色名称
- 添加了 `admin_setup.php`：输入管理员密钥即可升级用户

---

## Prompt 4：安全审查与整改

### 输入
> 对完成的权限控制中间件进行代码审查，重点关注：
> 1. 是否存在越权访问路径（不通过菜单直接访问 URL）
> 2. Session 安全性
> 3. 错误信息是否泄露敏感信息
> 4. 角色验证是否在服务端完成

### AI 输出要点
- 每个 Pass 的 index.php 顶部都做了服务端权限检查，直接访问 URL 也会被拦截
- 403 页面不泄露数据库或系统内部细节
- 角色信息存储在服务端的 users.json 中，客户端不可篡改
- 登录成功后 session_regenerate_id() 防固定攻击