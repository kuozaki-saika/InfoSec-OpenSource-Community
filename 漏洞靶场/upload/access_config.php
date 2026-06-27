<?php
/**
 * 权限控制配置
 * 定义角色等级和关卡访问权限
 */

// 角色等级（数值越大权限越高）
define('ROLE_LEVEL_USER', 1);
define('ROLE_LEVEL_ADMIN', 2);

// 关卡权限映射表
// key => 关卡ID, value => 最低所需角色等级
$pass_permissions = [
    'Pass-01' => ROLE_LEVEL_USER,
    'Pass-02' => ROLE_LEVEL_USER,
    'Pass-03' => ROLE_LEVEL_USER,
    'Pass-04' => ROLE_LEVEL_USER,
    'Pass-05' => ROLE_LEVEL_USER,
    'Pass-06' => ROLE_LEVEL_USER,
    'Pass-07' => ROLE_LEVEL_USER,
    'Pass-08' => ROLE_LEVEL_USER,
    'Pass-09' => ROLE_LEVEL_USER,
    'Pass-10' => ROLE_LEVEL_USER,
    'Pass-11' => ROLE_LEVEL_USER,
    'Pass-12' => ROLE_LEVEL_USER,
    'Pass-13' => ROLE_LEVEL_USER,
    'Pass-14' => ROLE_LEVEL_USER,
    'Pass-15' => ROLE_LEVEL_USER,
    'Pass-17' => ROLE_LEVEL_USER,
    'Pass-18' => ROLE_LEVEL_USER,
    'Pass-19' => ROLE_LEVEL_ADMIN,  // 高级关卡，仅管理员可访问
    'Pass-20' => ROLE_LEVEL_ADMIN,
    'Pass-21' => ROLE_LEVEL_ADMIN,
];