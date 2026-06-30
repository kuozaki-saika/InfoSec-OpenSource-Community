<?php
/**
 * 审计日志查看管理页面
 * 开发者：徐菱卿 (成员4)
 */
require_once __DIR__ . '/../common/Logger.php';

// 模拟权限控制（后续由成员2徐元昊的中间件接管）
session_start();
// if ($_SESSION['role'] !== 'admin') { die('Access Denied. Admins Only.'); }

// 执行完整性校验
$integrity = SecurityLogger::verifyIntegrity();

// 读取告警日志
$alerts = [];
$alert_file = __DIR__ . '/../data/security_alerts.log';
if (file_exists($alert_file)) {
    $alerts = array_slice(file($alert_file), -5); // 只取最新的5条告警
}

// 读取主审计日志
$log_file = __DIR__ . '/../data/security_audit.log';
$logs = [];
if (file_exists($log_file)) {
    $lines = file($log_file);
    foreach ($lines as $line) {
        $data = json_decode($line, true);
        if ($data) $logs[] = $data;
    }
    $logs = array_reverse($logs); // 最新的日志排在前面
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>upload-labs 安全审计控制台</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; }
        h2 { color: #2c3e50; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
        .status-card { padding: 15px; margin-bottom: 20px; border-radius: 4px; font-weight: bold; }
        .status-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-box { background: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 4px; }
        .alert-title { color: #856404; font-weight: bold; margin-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 4px; overflow: hidden; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #edf2f7; font-size: 14px; }
        th { background-color: #4a5568; color: #fff; }
        tr:hover { background-color: #f7fafc; }
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .badge-success { background: #c6f6d5; color: #22543d; }
        .badge-fail { background: #fed7d7; color: #742a2a; }
        .badge-info { background: #bee3f8; color: #2b6cb0; }
        pre { margin: 0; font-family: monospace; font-size: 12px; background: #edf2f7; padding: 4px; border-radius: 3px; }
    </style>
</head>
<body>
<div class="container">
    <h2>🛡️ upload-labs 安全审计控制台 (徐菱卿-PR)</h2>

    <?php if ($integrity['is_valid']): ?>
        <div class="status-card status-success"> ✓ 日志完整性校验通过：未检测到日志篡改或非法删除。</div>
    <?php else: ?>
        <div class="status-card status-danger"> ❌ 警告：检测到日志完整性破坏！第 <?php echo $integrity['corrupted_line']; ?> 行数据遭遇篡改或链条断裂！</div>
    <?php endif; ?>

    <?php if (!empty($alerts)): ?>
        <div class="alert-box">
            <div class="alert-title">⚠️ 实时入侵防护告警 (最近5条)</div>
            <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #856404;">
                <?php foreach ($alerts as $alert): ?>
                    <li><?php echo htmlspecialchars($alert); ?></li>
                <?php endforeach; ?>
            </ul>
        </div>
    <?php endif; ?>

    <h3>操作日志明细</h3>
    <table>
        <thead>
            <tr>
                <th>时间</th>
                <th>操作用户</th>
                <th>事件类型</th>
                <th>状态</th>
                <th>IP地址</th>
                <th>附加详情</th>
            </tr>
        </thead>
        <tbody>
            <?php if (empty($logs)): ?>
                <tr><td colspan="6" style="text-align: center; color: #aaa;">暂无审计日志记录</td></tr>
            <?php else: ?>
                <?php foreach ($logs as $log): ?>
                    <tr>
                        <td><?php echo $log['timestamp']; ?></td>
                        <td><strong><?php echo htmlspecialchars($log['username']); ?></strong></td>
                        <td><span class="badge badge-info"><?php echo $log['action']; ?></span></td>
                        <td>
                            <span class="badge <?php echo $log['status'] === 'SUCCESS' ? 'badge-success' : 'badge-fail'; ?>">
                                <?php echo $log['status']; ?>
                            </span>
                        </td>
                        <td><?php echo $log['ip']; ?></td>
                        <td><pre><?php echo json_encode($log['details'], JSON_UNESCAPED_UNICODE); ?></pre></td>
                    </tr>
                <?php endforeach; ?>
            <?php endif; ?>
        </tbody>
    </table>
</div>
</body>
</html>
