<?php
include '../config.php';
include '../head.php';
include '../menu.php';
require_once __DIR__ . '/../access_control.php';
check_pass_access('Pass-19');


$is_upload = false;
$msg = null;
if (isset($_POST['submit']))
{
    require_once("./myupload.php");
    $imgFileName =time();
    $u = new MyUpload($_FILES['upload_file']['name'], $_FILES['upload_file']['tmp_name'], $_FILES['upload_file']['size'],$imgFileName);
    $status_code = $u->upload(UPLOAD_PATH);
    switch ($status_code) {
        case 1:
            $is_upload = true;
            $img_path = $u->cls_upload_dir . $u->cls_file_rename_to;
            break;
        case 2:
            $msg = '鏂囦欢宸茬粡琚笂浼狅紝浣嗘病鏈夐噸鍛藉悕銆?;
            break; 
        case -1:
            $msg = '杩欎釜鏂囦欢涓嶈兘涓婁紶鍒版湇鍔″櫒鐨勪复鏃舵枃浠跺瓨鍌ㄧ洰褰曘€?;
            break; 
        case -2:
            $msg = '涓婁紶澶辫触锛屼笂浼犵洰褰曚笉鍙啓銆?;
            break; 
        case -3:
            $msg = '涓婁紶澶辫触锛屾棤娉曚笂浼犺绫诲瀷鏂囦欢銆?;
            break; 
        case -4:
            $msg = '涓婁紶澶辫触锛屼笂浼犵殑鏂囦欢杩囧ぇ銆?;
            break; 
        case -5:
            $msg = '涓婁紶澶辫触锛屾湇鍔″櫒宸茬粡瀛樺湪鐩稿悓鍚嶇О鏂囦欢銆?;
            break; 
        case -6:
            $msg = '鏂囦欢鏃犳硶涓婁紶锛屾枃浠朵笉鑳藉鍒跺埌鐩爣鐩綍銆?;
            break;      
        default:
            $msg = '鏈煡閿欒锛?;
            break;
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
            <form enctype="multipart/form-data" method="post">
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