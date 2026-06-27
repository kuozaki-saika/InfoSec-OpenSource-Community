<?php
include '../config.php';
include '../head.php';
include '../menu.php';
require_once __DIR__ . '/../access_control.php';
check_pass_access('Pass-13');


$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $ext_arr = array('jpg','png','gif');
    $file_ext = substr($_FILES['upload_file']['name'],strrpos($_FILES['upload_file']['name'],".")+1);
    if(in_array($file_ext,$ext_arr)){
        $temp_file = $_FILES['upload_file']['tmp_name'];
        $img_path = $_POST['save_path']."/".rand(10, 99).date("YmdHis").".".$file_ext;

        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = "涓婁紶澶辫触";
        }
    } else {
        $msg = "鍙厑璁镐笂浼?jpg|.png|.gif绫诲瀷鏂囦欢锛?;
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
                <input type="hidden" name="save_path" value="../upload/"/>
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