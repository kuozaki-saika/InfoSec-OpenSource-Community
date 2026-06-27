<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if ($username === '' || $password === '') {
        $error = '用户名和密码不能为空';
    } elseif (strlen($username) > 32) {
        $error = '用户名过长';
    } else {
        $user = find_user($username);
        if ($user && password_verify($password, $user['password'])) {
            session_regenerate_id(true);
            $_SESSION['user'] = $user['username'];
            header('Location: ' . APP_URL_ROOT . '/index.php');
            exit;
        }
        $error = '用户名或密码错误';
    }
}
include 'head.php';
?>
<div id="upload_panel">
    <h3>登录</h3>
    <?php if ($error): ?>
        <p style="color:red"><?php echo htmlspecialchars($error); ?></p>
    <?php endif; ?>
    <form method="post">
        <p>用户名: <input type="text" name="username" maxlength="32"></p>
        <p>密码: <input type="password" name="password"></p>
        <p><input type="submit" value="登录"></p>
    </form>
    <p>没有账号？<a href="register.php">注册</a></p>
</div>
<?php include 'footer.php'; ?>
