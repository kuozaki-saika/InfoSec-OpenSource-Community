<div id="menu">     
	<ul id="menulist">
<?php
require_once __DIR__ . '/access_config.php';
$accessible = get_accessible_passes();
function is_accessible($pass_id) {
    global $accessible;
    return in_array($pass_id, $accessible);
}
?>
		<li><a id="Pass-01" href="<?php echo APP_URL_ROOT;?>/Pass-01/index.php">Pass-01</a></li> 
		<li><a id="Pass-02" href="<?php echo APP_URL_ROOT;?>/Pass-02/index.php">Pass-02</a></li> 
		<li><a id="Pass-03" href="<?php echo APP_URL_ROOT;?>/Pass-03/index.php">Pass-03</a></li> 
		<li><a id="Pass-04" href="<?php echo APP_URL_ROOT;?>/Pass-04/index.php">Pass-04</a></li> 
		<li><a id="Pass-05" href="<?php echo APP_URL_ROOT;?>/Pass-05/index.php">Pass-05</a></li> 
		<li><a id="Pass-06" href="<?php echo APP_URL_ROOT;?>/Pass-06/index.php">Pass-06</a></li> 
		<li><a id="Pass-07" href="<?php echo APP_URL_ROOT;?>/Pass-07/index.php">Pass-07</a></li> 
		<li><a id="Pass-08" href="<?php echo APP_URL_ROOT;?>/Pass-08/index.php">Pass-08</a></li> 
		<li><a id="Pass-09" href="<?php echo APP_URL_ROOT;?>/Pass-09/index.php">Pass-09</a></li> 
		<li><a id="Pass-10" href="<?php echo APP_URL_ROOT;?>/Pass-10/index.php">Pass-10</a></li> 
		<li><a id="Pass-11" href="<?php echo APP_URL_ROOT;?>/Pass-11/index.php">Pass-11</a></li> 
		<li><a id="Pass-12" href="<?php echo APP_URL_ROOT;?>/Pass-12/index.php">Pass-12</a></li> 
		<li><a id="Pass-13" href="<?php echo APP_URL_ROOT;?>/Pass-13/index.php">Pass-13</a></li> 
		<li><a id="Pass-14" href="<?php echo APP_URL_ROOT;?>/Pass-14/index.php">Pass-14</a></li> 
		<li><a id="Pass-15" href="<?php echo APP_URL_ROOT;?>/Pass-15/index.php">Pass-15</a></li> 
		<li><a id="Pass-17" href="<?php echo APP_URL_ROOT;?>/Pass-17/index.php">Pass-17</a></li> 
		<li><a id="Pass-18" href="<?php echo APP_URL_ROOT;?>/Pass-18/index.php">Pass-18</a></li> 
<?php if (is_accessible('Pass-19')): ?>
		<li><a id="Pass-19" href="<?php echo APP_URL_ROOT;?>/Pass-19/index.php">Pass-19</a></li>
<?php else: ?>
		<li><span style="color:#888;cursor:default" title="需要管理员权限">Pass-19 🔒</span></li>
<?php endif; ?>
<?php if (is_accessible('Pass-20')): ?>
		<li><a id="Pass-20" href="<?php echo APP_URL_ROOT;?>/Pass-20/index.php">Pass-20</a></li>
<?php else: ?>
		<li><span style="color:#888;cursor:default" title="需要管理员权限">Pass-20 🔒</span></li>
<?php endif; ?>
<?php if (is_accessible('Pass-21')): ?>
        <li><a id="Pass-21" href="<?php echo APP_URL_ROOT;?>/Pass-21/index.php">Pass-21</a></li>
<?php else: ?>
        <li><span style="color:#888;cursor:default" title="需要管理员权限">Pass-21 🔒</span></li>
<?php endif; ?>
	</ul> 
</div>