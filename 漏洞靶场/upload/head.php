<?php
$current = basename($_SERVER['SCRIPT_NAME']);
if ($current !== 'login.php' && $current !== 'register.php') {
    require_login();
}
?>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
	<link rel="icon" type="image/x-icon" href="<?php echo APP_URL_ROOT;?>/img/favicon.png" />  
	<title>upload-labs</title>
</head>
<link rel="stylesheet" type="text/css" href="<?php echo APP_URL_ROOT;?>/css/index.css">
<link rel="stylesheet" type="text/css" href="<?php echo APP_URL_ROOT;?>/css/prism.css">
<body>
	<div id="head">
		<a href="<?php echo APP_URL_ROOT;?>/"><img src="<?php echo APP_URL_ROOT;?>/img/logo.png"/></a>
		<div id="head_menu">
			<a id="handle_code" href="javascript:show_code()">显示源码</a>
			<a href="javascript:get_prompt()">查看提示</a>
			<a href="javascript:clean_upload_file()">清空上传文件</a>
			<?php if (isset($_SESSION['auth_user'])): 
			    $role_name = (get_current_role() === ROLE_ADMIN) ? '管理员' : '用户';
			?>
				<span style="color:#fff;margin-left:12px"><?php echo htmlspecialchars($_SESSION['auth_user']); ?><small style="color:#9cf;margin-left:4px">(<?php echo $role_name; ?>)</small></span>
				<a href="<?php echo APP_URL_ROOT;?>/admin_setup.php">管理</a>
				<a href="<?php echo APP_URL_ROOT;?>/logout.php">退出</a>
			<?php endif; ?>
		</div>
	</div>
	<div id="main">