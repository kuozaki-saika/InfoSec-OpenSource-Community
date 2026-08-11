<?php
/**
 * 权限控制中间件
 * 提供角色检查和关卡访问控制功能
 * 依赖：auth.php, access_config.php
 */
require_once __DIR__ . '/access_config.php';

/**
 * 将角色名转为等级数值
 */
function role_to_level($role) {
    switch ($role) {
        case ROLE_ADMIN: return ROLE_LEVEL_ADMIN;
        default: return ROLE_LEVEL_USER;
    }
}

/**
 * 获取当前用户角色等级
 */
function get_current_role_level() {
    if (!isset($_SESSION['auth_user'])) return 0;
    $user = find_user($_SESSION['auth_user']);
    if (!$user) return 0;
    return role_to_level($user['role'] ?? ROLE_USER);
}

/**
 * 要求当前用户至少达到指定角色等级
 * @param string $min_role 最低角色名（ROLE_USER 或 ROLE_ADMIN）
 */
function require_role($min_role) {
    require_login();
    $min_level = role_to_level($min_role);
    $current_level = get_current_role_level();
    if ($current_level < $min_level) {
        header('HTTP/1.1 403 Forbidden');
        include __DIR__ . '/403.php';
        exit;
    }
}

/**
 * 检查是否有权访问指定关卡
 * @param string $pass_id 关卡ID，如 'Pass-02'
 */
function check_pass_access($pass_id) {
    global $pass_permissions;
    $min_level = $pass_permissions[$pass_id] ?? ROLE_LEVEL_USER;
    require_login();
    $current_level = get_current_role_level();
    if ($current_level < $min_level) {
        header('HTTP/1.1 403 Forbidden');
        include __DIR__ . '/403.php';
        exit;
    }
}

/**
 * 获取当前用户可以访问的关卡列表
 * @return array
 */
function get_accessible_passes() {
    global $pass_permissions;
    $user_level = get_current_role_level();
    $accessible = [];
    foreach ($pass_permissions as $pass => $min_level) {
        if ($user_level >= $min_level) {
            $accessible[] = $pass;
        }
    }
    return $accessible;
}