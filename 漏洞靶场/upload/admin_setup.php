<?php
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/auth.php';

if (!isset($_SESSION['auth_user'])) {
    header('Location: ' . APP_URL_ROOT . '/login.php');
    exit;
}

$msg = '';

// 处理提权请求
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['promote_user'], $_POST['admin_secret'])) {
    if ($_POST['admin_secret'] !== ADMIN_SECRET) {
        $msg = '管理员密钥错误';
    } else {
        $target = trim($_POST['promote_user']);
        $users = get_users();
        foreach ($users as &$u) {
            if ($u['username'] === $target) {
                $u['role'] = ROLE_ADMIN;
                $msg = "用户 {$target} 已升级为管理员";
                break;
            }
        }
        unset($u);
        save_users($users);
    }
}
include 'head.php';
?>
<div id="upload_panel">
    <h3>管理员设置</h3>
    <?php if ($msg): ?>
        <p style="color:green"><?php echo htmlspecialchars($msg); ?></p>
    <?php endif; ?>
    <form method="post">
        <p>管理员密钥: <input type="password" name="admin_secret" required></p>
        <p>目标用户:
        <select name="promote_user">
            <?php
            $users = get_users();
            foreach ($users as $u) {
                $selected = ($u['username'] === $_SESSION['auth_user']) ? ' selected' : '';
                echo '<option value="' . htmlspecialchars($u['username']) . '"' . $selected . '>' . htmlspecialchars($u['username']) . ' (' . htmlspecialchars($u['role'] ?? 'user') . ')</option>';
            }
            ?>
        </select></p>
        <p><input type="submit" value="升级为管理员"></p>
    </form>
    <p><a href="<?php echo APP_URL_ROOT;?>/index.php">返回首页</a></p>
</div>
<?php include 'footer.php'; ?>