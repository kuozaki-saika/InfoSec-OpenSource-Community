<?php
header("Content-type: text/html;charset=utf-8");
error_reporting(0);

define("WWW_ROOT",$_SERVER["DOCUMENT_ROOT"]);
define("APP_ROOT",str_replace("\\","/",dirname(__FILE__)));
define("APP_URL_ROOT",str_replace(WWW_ROOT,"",APP_ROOT));
define("INC_VUL_PATH",APP_URL_ROOT . "/include.php");
define("UPLOAD_PATH", "../upload");
define("ADMIN_SECRET", "InfoSec2024_AdminKey");

require_once __DIR__ . "/auth.php";
?>