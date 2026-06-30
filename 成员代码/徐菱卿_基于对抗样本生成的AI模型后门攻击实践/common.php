<?php
/**
 * upload-labs 安全审计日志系统
 * 开发者：徐菱卿 (成员4)
 * 安全控制点：日志完整性、敏感信息脱敏、异常行为记录与告警
 */

class SecurityLogger {
    private static $log_file = __DIR__ . '/../data/security_audit.log';
    private static $alert_threshold = 5; // 触发告警的连续登录失败次数

    /**
     * 核心记录方法
     * @param string $username 用户名
     * @param string $action 操作类型 (LOGIN_SUCCESS, LOGIN_FAIL, FILE_UPLOAD, VIEW_SOURCE)
     * @param string $status 结果 (SUCCESS / FAIL)
     * @param array $details 详情数据
     */
    public static function log($username, $action, $status, $details = []) {
        // 1. 敏感数据脱敏（防止日志泄露密码）
        if (isset($details['password'])) {
            $details['password'] = '******';
        }
        if (isset($details['pass_token'])) {
            $details['pass_token'] = '******';
        }

        $log_dir = dirname(self::$log_file);
        if (!is_dir($log_dir)) {
            mkdir($log_dir, 0755, true);
        }

        // 2. 获取前一条日志的 Hash（构建防篡改 Hash 链）
        $prev_hash = '00000000000000000000000000000000';
        if (file_exists(self::$log_file)) {
            $lines = file(self::$log_file);
            if (!empty($lines)) {
                $last_line = json_decode(end($lines), true);
                if (isset($last_line['hash'])) {
                    $prev_hash = $last_line['hash'];
                }
            }
        }

        // 3. 构造日志主体
        $log_entry = [
            'timestamp'  => date('Y-m-d H:i:s'),
            'username'   => empty($username) ? 'GUEST' : htmlspecialchars($username),
            'action'     => $action,
            'status'     => $status,
            'ip'         => self::getIp(),
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown',
            'details'    => $details,
            'prev_hash'  => $prev_hash
        ];

        // 4. 计算当前日志的 Hash 值，用于防篡改校验
        $serialize_data = $log_entry['timestamp'] . $log_entry['username'] . $log_entry['action'] . $log_entry['status'] . $log_entry['prev_hash'];
        $log_entry['hash'] = hash('sha256', $serialize_data);

        // 5. 写入文件（追加模式，加锁防止并发冲突）
        file_put_contents(self::$log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);

        // 6. 异常行为告警检查
        if ($action === 'LOGIN_FAIL') {
            self::checkBruteForce($username);
        }
    }

    /**
     * 暴力破解/异常行为告警检查
     */
    private static function checkBruteForce($username) {
        if (!file_exists(self::$log_file)) return;

        $lines = file(self::$log_file);
        $fail_count = 0;
        $time_window = 300; // 5分钟窗口
        $now = time();

        // 逆序检查最近的日志
        for ($i = count($lines) - 1; $i >= 0; $i--) {
            $log = json_decode($lines[$i], true);
            if (!$log) continue;

            if ((($now - strtotime($log['timestamp'])) < $time_window)) {
                if ($log['action'] === 'LOGIN_FAIL' && $log['username'] === $username) {
                    $fail_count++;
                } elseif ($log['action'] === 'LOGIN_SUCCESS' && $log['username'] === $username) {
                    // 如果中途有成功登录，中断连续计数
                    break;
                }
            } else {
                break; // 超出时间窗口
            }
        }

        if ($fail_count >= self::$alert_threshold) {
            // 触发告警机制：向特殊告警日志写入，或设置 Session 触发前端警告
            $alert_file = dirname(self::$log_file) . '/security_alerts.log';
            $alert_msg = sprintf("[%s] ALERT: User [%s] triggered Brute Force protection. Failures: %d inside 5m. IP: %s\n", 
                date('Y-m-d H:i:s'), $username, $fail_count, self::getIp());
            file_put_contents($alert_file, $alert_msg, FILE_APPEND | LOCK_EX);
        }
    }

    /**
     * 验证日志文件完整性（防黑客擦除日志）
     * @return array [bool 'is_valid', int 'corrupted_line']
     */
    public static function verifyIntegrity() {
        if (!file_exists(self::$log_file)) return ['is_valid' => true, 'corrupted_line' => -1];

        $lines = file(self::$log_file);
        $expected_prev_hash = '00000000000000000000000000000000';

        foreach ($lines as $index => $line) {
            $log = json_decode($line, true);
            if (!$log) return ['is_valid' => false, 'corrupted_line' => $index + 1];

            // 验证 Hash 链
            if ($log['prev_hash'] !== $expected_prev_hash) {
                return ['is_valid' => false, 'corrupted_line' => $index + 1];
            }

            // 重新计算 Hash 验证本条是否被篡改
            $serialize_data = $log['timestamp'] . $log['username'] . $log['action'] . $log['status'] . $log['prev_hash'];
            $calculated_hash = hash('sha256', $serialize_data);

            if ($log['hash'] !== $calculated_hash) {
                return ['is_valid' => false, 'corrupted_line' => $index + 1];
            }

            $expected_prev_hash = $log['hash'];
        }

        return ['is_valid' => true, 'corrupted_line' => -1];
    }

    private static function getIp() {
        return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
    }
}
