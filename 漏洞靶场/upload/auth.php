<?php
session_start();

define('USERS_FILE', __DIR__ . '/users.json');

define('ROLE_USER', 'user');
define('ROLE_ADMIN', 'admin');

if (!file_exists(USERS_FILE)) {
    file_put_contents(USERS_FILE, json_encode([]));
}

function get_users() {
    return json_decode(file_get_contents(USERS_FILE), true);
}

function save_users($users) {
    file_put_contents(USERS_FILE, json_encode($users, JSON_PRETTY_PRINT));
}

function find_user($username) {
    $users = get_users();
    foreach ($users as $u) {
        if ($u['username'] === $username) return $u;
    }
    return null;
}

function create_user($username, $password) {
    $users = get_users();
    $users[] = [
        'username' => $username,
        'password' => password_hash($password, PASSWORD_BCRYPT),
        'role' => ROLE_USER,
        'created_at' => date('Y-m-d H:i:s')
    ];
    save_users($users);
}

function create_user_with_role($username, $password, $role = ROLE_USER) {
    $users = get_users();
    $users[] = [
        'username' => $username,
        'password' => password_hash($password, PASSWORD_BCRYPT),
        'role' => $role,
        'created_at' => date('Y-m-d H:i:s')
    ];
    save_users($users);
}

function require_login() {
    if (!isset($_SESSION['auth_user'])) {
        header('Location: ' . APP_URL_ROOT . '/login.php');
        exit;
    }
}

function get_current_user() {
    if (!isset($_SESSION['auth_user'])) return null;
    return find_user($_SESSION['auth_user']);
}

function get_current_role() {
    $user = get_current_user();
    if (!$user) return null;
    return $user['role'] ?? ROLE_USER;
}