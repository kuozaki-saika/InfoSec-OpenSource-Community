<?php
session_start();

define("ROLE_USER", "user");
define("ROLE_ADMIN", "admin");

define("USERS_FILE", __DIR__ . "/users.json");

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
        if ($u["username"] === $username) return $u;
    }
    return null;
}

function create_user($username, $password) {
    $users = get_users();
    $users[] = array(
        "username" => $username,
        "password" => password_hash($password, PASSWORD_BCRYPT),
        "role" => ROLE_USER,
        "created_at" => date("Y-m-d H:i:s")
    );
    save_users($users);
}

function require_login() {
    if (!isset($_SESSION["auth_user"])) {
        header("Location: " . APP_URL_ROOT . "/login.php");
        exit;
    }
}

function get_auth_user() {
    if (!isset($_SESSION["auth_user"])) return null;
    return find_user($_SESSION["auth_user"]);
}

function get_current_role() {
    $user = get_auth_user();
    if (!$user) return null;
    return (isset($user["role"])) ? $user["role"] : ROLE_USER;
}

function get_role_name() {
    $role = get_current_role();
    if ($role === ROLE_ADMIN) return "Admin";
    return "User";
}
?>