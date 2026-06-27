<?php
include '../config.php';
include '../common.php';
include '../head.php';
include '../menu.php';
require_once __DIR__ . '/../access_control.php';
check_pass_access('Pass-21');



if (isset($_POST['submit'])) {
    if (file_exists(UPLOAD_PATH)) {

        $is_upload = false;
        $msg = null;
        if(!empty($_FILES['upload_file'])){
            //mime check
            $allow_type = array('image/jpeg','image/png','image/gif');
            if(!in_array($_FILES['upload_file']['type'],$allow_type)){
                $msg = "绂佹涓婁紶璇ョ被鍨嬫枃浠?";
            }else{
                //check filename
                $file = empty($_POST['save_name']) ? $_FILES['upload_file']['name'] : $_POST['save_name'];
                if (!is_array($file)) {
                    $file = explode('.', strtolower($file));
                }

                $ext = end($file);
                $allow_suffix = array('jpg','png','gif');
                if (!in_array($ext, $allow_suffix)) {
                    $msg = "绂佹涓婁紶璇ュ悗缂€鏂囦欢!";
                }else{
                    $file_name = reset($file) . '.' . $file[count($file) - 1];
                    $temp_file = $_FILES['upload_file']['tmp_name'];
                    $img_path = UPLOAD_PATH . '/' .$file_name;
                    if (move_uploaded_file($temp_file, $img_path)) {
                        $msg = "鏂囦欢涓婁紶鎴愬姛锛?;
                        $is_upload = true;
                    } else {
                        $msg = "鏂囦欢涓婁紶澶辫触锛?;
                    }
                }
            }
        }else{
            $msg = "璇烽€夋嫨瑕佷笂浼犵殑鏂囦欢锛?;
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
            <form enctype="multipart/form-data" method="post">
                <p>璇烽€夋嫨瑕佷笂浼犵殑鍥剧墖锛?p>
                <input class="input_file" type="file" name="upload_file"/>
                <p>淇濆瓨鍚嶇О:<p>
                <input class="input_text" type="text" name="save_name" value="upload-20.jpg" /><br/>
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