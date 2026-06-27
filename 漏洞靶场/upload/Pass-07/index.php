<?php
include '../config.php';
include '../common.php';
include '../head.php';
include '../menu.php';
require_once __DIR__ . '/../access_control.php';
check_pass_access('Pass-07');


$is_upload = false;
$msg = null;
if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {
        $deny_ext = array(".php",".php5",".php4",".php3",".php2",".html",".htm",".phtml",".pht",".pHp",".pHp5",".pHp4",".pHp3",".pHp2",".Html",".Htm",".pHtml",".jsp",".jspa",".jspx",".jsw",".jsv",".jspf",".jtml",".jSp",".jSpx",".jSpa",".jSw",".jSv",".jSpf",".jHtml",".asp",".aspx",".asa",".asax",".ascx",".ashx",".asmx",".cer",".aSp",".aSpx",".aSa",".aSax",".aScx",".aShx",".aSmx",".cEr",".sWf",".swf",".htaccess",".ini");
        $file_name = $_FILES['upload_file']['name'];
        $file_name = deldot($file_name);//鍒犻櫎鏂囦欢鍚嶆湯灏剧殑鐐?
        $file_ext = strrchr($file_name, '.');
        $file_ext = strtolower($file_ext); //杞崲涓哄皬鍐?
        $file_ext = str_ireplace('::$DATA', '', $file_ext);//鍘婚櫎瀛楃涓?:$DATA
        
        if (!in_array($file_ext, $deny_ext)) {
            $temp_file = $_FILES['upload_file']['tmp_name'];
            $img_path = UPLOAD_PATH.'/'.date("YmdHis").rand(1000,9999).$file_ext;
            if (move_uploaded_file($temp_file,$img_path)) {
                $is_upload = true;
            } else {
                $msg = '涓婁紶鍑洪敊锛?;
            }
        } else {
            $msg = '姝ゆ枃浠朵笉鍏佽涓婁紶';
        }
    } else {
        $msg = UPLOAD_PATH . '鏂囦欢澶逛笉瀛樺湪,璇锋墜宸ュ垱寤猴紒';
    }
}
?>

<div id="upload_panel">
    <ol>
        <li>
            <h3>浠诲姟</h3>
            <p>涓婁紶涓€涓?code>webshell</code>鍒版湇鍔″櫒銆?/p>
        </li>
        <li>
            <h3>涓婁紶鍖?/h3>
            <form enctype="multipart/form-data" method="post" onsubmit="return checkFile()">
                <p>璇烽€夋嫨瑕佷笂浼犵殑鍥剧墖锛?p>
                <input class="input_file" type="file" name="upload_file"/>
                <input class="button" type="submit" name="submit" value="涓婁紶"/>
            </form>
            <div id="msg">
                <?php 
                    if($msg != null){
                        echo "鎻愮ず锛?.$msg;
                    }
                ?>
            </div>
            <div id="img">
                <?php
                    if($is_upload){
                        echo '<img src="'.$img_path.'" width="250px" />';
                    }
                ?>
            </div>
        </li>
        <?php 
            if($_GET['action'] == "show_code"){
                include 'show_code.php';
            }
        ?>
    </ol>
</div>

<?php
include '../footer.php';
?>