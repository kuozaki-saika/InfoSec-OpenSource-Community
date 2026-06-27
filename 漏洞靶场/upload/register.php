<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if ($username === '' || $password === '') {
        $error = '用户名和密码不能为空';
    } elseif (strlen($username) < 3 || strlen($username) > 32) {
        $error = '用户名需 3-32 个字符';
    } elseif (strlen($password) < 6) {
        $error = '密码至少 6 位';
    } elseif (!preg_match('/^[a-zA-Z0-9_]+$/', $username)) {
        $error = '用户名只能包含字母、数字和下划线';
    } elseif (find_user($username)) {
        $error = '用户名已存在';
    } else {
        create_user($username, $password);
        header('Location: login.php');
        exit;
    }
}
include 'head.php';
?>
<div id="upload_panel">
    <h3>注册</h3>
    <?php if ($error): ?>
        <p style="color:red"><?php echo htmlspecialchars($error); ?></p>
    <?php endif; ?>
    <form method="post">
        <p>用户名: <input type="text" name="username" maxlength="32"></p>
        <p>密码: <input type="password" name="password"></p>
        <p><input type="submit" value="注册"></p>
    </form>
    <p>已有账号？<a href="login.php">登录</a></p>
</div>
<?php include 'footer.php'; ?>
