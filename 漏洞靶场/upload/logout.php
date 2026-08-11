<?php
session_start();
$_SESSION = [];
session_destroy();
header('Location: ' . APP_URL_ROOT . '/login.php');
