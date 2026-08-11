# 整改前后对比 (Before-After Diff)

## 模块：Upload-Labs 权限控制中间件
## 对比基准：林翔/靶场认证系统 分支
## 对比目标：徐元昊/权限控制中间件 分支

---

## 1. 新增文件

| 文件 | 行数 | 功能 |
|------|------|------|
| access_config.php | 35 | 角色等级定义 + 关卡权限映射 |
| access_control.php | 72 | 访问控制中间件函数 |
| 403.php | 35 | 权限不足提示页 |
| admin_setup.php | 40 | 管理员升级页 |

## 2. 修改文件

### auth.php
```
+ define('ROLE_USER', 'user');
+ define('ROLE_ADMIN', 'admin');
+ create_user() → 添加 role 字段
+ create_user_with_role()
+ get_current_user()
+ get_current_role()
```

### head.php
```
+ 用户名旁显示 "(用户)" 或 "(管理员)"
+ 增加 "管理" 链接到 admin_setup.php
```

### menu.php
```
+ require_once access_config.php
+ get_accessible_passes()
+ Pass-19/20/21 根据角色动态显示或加锁
```

### Pass-02 ~ Pass-21/index.php
```
+ require_once __DIR__ . '/../access_control.php';
+ check_pass_access('Pass-XX');
```

## 3. 安全提升对比

| 方面 | 修改前 | 修改后 |
|------|--------|--------|
| 权限分级 | 无（登录/未登录） | user + admin 两级 |
| 高级关卡保护 | 无（任何用户可访问） | 仅管理员可访问 |
| 菜单指示 | 全部显示 | 锁定关卡显示 🔒 |
| 服务端检查 | 无 | 每个 Pass 独立检查 |
| 越权防护 | 无 | URL 直接访问也被拦截 |
| 管理员管理 | 无 | admin_setup.php 密钥升级 |