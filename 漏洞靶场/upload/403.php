<?php
/**
 * 403 Forbidden 页面
 * 用户权限不足时显示
 */
require_once __DIR__ . '/config.php';
?><!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>权限不足 - upload-labs</title>
    <link rel="stylesheet" type="text/css" href="<?php echo APP_URL_ROOT;?>/css/index.css">
    <style>
        .error-container { text-align: center; padding: 80px 20px; }
        .error-code { font-size: 72px; font-weight: bold; color: #e74c3c; margin-bottom: 10px; }
        .error-msg { font-size: 18px; color: #555; margin-bottom: 30px; }
        .error-desc { font-size: 14px; color: #888; margin-bottom: 30px; line-height: 1.8; }
        .btn-back { display: inline-block; padding: 10px 24px; background: #3498db; color: #fff; text-decoration: none; border-radius: 4px; }
        .btn-back:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div id="main">
        <div class="error-container">
            <div class="error-code">403</div>
            <div class="error-msg">权限不足，无法访问此关卡</div>
            <div class="error-desc">
                当前账号需要更高的权限等级才能访问该页面。<br>
                如果你是 <?php echo htmlspecialchars($_SESSION['auth_user'] ?? ''); ?>，请联系管理员升级账号权限。
            </div>
            <a class="btn-back" href="<?php echo APP_URL_ROOT;?>/index.php">返回首页</a>
        </div>
    </div>
</body>
</html>