<?php
include '../config.php';
include '../head.php';
include '../menu.php';
require_once __DIR__ . '/../access_control.php';
check_pass_access('Pass-17');


$is_upload = false;
$msg = null;
if (isset($_POST['submit'])){
    // 鑾峰緱涓婁紶鏂囦欢鐨勫熀鏈俊鎭紝鏂囦欢鍚嶏紝绫诲瀷锛屽ぇ灏忥紝涓存椂鏂囦欢璺緞
    $filename = $_FILES['upload_file']['name'];
    $filetype = $_FILES['upload_file']['type'];
    $tmpname = $_FILES['upload_file']['tmp_name'];

    $target_path=UPLOAD_PATH.'/'.basename($filename);

    // 鑾峰緱涓婁紶鏂囦欢鐨勬墿灞曞悕
    $fileext= substr(strrchr($filename,"."),1);

    //鍒ゆ柇鏂囦欢鍚庣紑涓庣被鍨嬶紝鍚堟硶鎵嶈繘琛屼笂浼犳搷浣?
    if(($fileext == "jpg") && ($filetype=="image/jpeg")){
        if(move_uploaded_file($tmpname,$target_path)){
            //浣跨敤涓婁紶鐨勫浘鐗囩敓鎴愭柊鐨勫浘鐗?
            $im = imagecreatefromjpeg($target_path);

            if($im == false){
                $msg = "璇ユ枃浠朵笉鏄痡pg鏍煎紡鐨勫浘鐗囷紒";
                @unlink($target_path);
            }else{
                //缁欐柊鍥剧墖鎸囧畾鏂囦欢鍚?
                srand(time());
                $newfilename = strval(rand()).".jpg";
                //鏄剧ず浜屾娓叉煋鍚庣殑鍥剧墖锛堜娇鐢ㄧ敤鎴蜂笂浼犲浘鐗囩敓鎴愮殑鏂板浘鐗囷級
                $img_path = UPLOAD_PATH.'/'.$newfilename;
                imagejpeg($im,$img_path);
                @unlink($target_path);
                $is_upload = true;
            }
        } else {
            $msg = "涓婁紶鍑洪敊锛?;
        }

    }else if(($fileext == "png") && ($filetype=="image/png")){
        if(move_uploaded_file($tmpname,$target_path)){
            //浣跨敤涓婁紶鐨勫浘鐗囩敓鎴愭柊鐨勫浘鐗?
            $im = imagecreatefrompng($target_path);

            if($im == false){
                $msg = "璇ユ枃浠朵笉鏄痯ng鏍煎紡鐨勫浘鐗囷紒";
                @unlink($target_path);
            }else{
                 //缁欐柊鍥剧墖鎸囧畾鏂囦欢鍚?
                srand(time());
                $newfilename = strval(rand()).".png";
                //鏄剧ず浜屾娓叉煋鍚庣殑鍥剧墖锛堜娇鐢ㄧ敤鎴蜂笂浼犲浘鐗囩敓鎴愮殑鏂板浘鐗囷級
                $img_path = UPLOAD_PATH.'/'.$newfilename;
                imagepng($im,$img_path);

                @unlink($target_path);
                $is_upload = true;               
            }
        } else {
            $msg = "涓婁紶鍑洪敊锛?;
        }

    }else if(($fileext == "gif") && ($filetype=="image/gif")){
        if(move_uploaded_file($tmpname,$target_path)){
            //浣跨敤涓婁紶鐨勫浘鐗囩敓鎴愭柊鐨勫浘鐗?
            $im = imagecreatefromgif($target_path);
            if($im == false){
                $msg = "璇ユ枃浠朵笉鏄痝if鏍煎紡鐨勫浘鐗囷紒";
                @unlink($target_path);
            }else{
                //缁欐柊鍥剧墖鎸囧畾鏂囦欢鍚?
                srand(time());
                $newfilename = strval(rand()).".gif";
                //鏄剧ず浜屾娓叉煋鍚庣殑鍥剧墖锛堜娇鐢ㄧ敤鎴蜂笂浼犲浘鐗囩敓鎴愮殑鏂板浘鐗囷級
                $img_path = UPLOAD_PATH.'/'.$newfilename;
                imagegif($im,$img_path);

                @unlink($target_path);
                $is_upload = true;
            }
        } else {
            $msg = "涓婁紶鍑洪敊锛?;
        }
    }else{
        $msg = "鍙厑璁镐笂浼犲悗缂€涓?jpg|.png|.gif鐨勫浘鐗囨枃浠讹紒";
    }
}
?>

<div id="upload_panel">
    <ol>
        <li>
            <h3>浠诲姟</h3>
            <p>涓婁紶<code>鍥剧墖椹?/code>鍒版湇鍔″櫒銆?/p>
            <p>娉ㄦ剰锛?/p>
            <p>1.淇濊瘉涓婁紶鍚庣殑鍥剧墖椹腑浠嶇劧鍖呭惈瀹屾暣鐨?code>涓€鍙ヨ瘽</code>鎴?code>webshell</code>浠ｇ爜銆?/p>
            <p>2.浣跨敤<a href="<?php echo INC_VUL_PATH;?>" target="_bank">鏂囦欢鍖呭惈婕忔礊</a>鑳借繍琛屽浘鐗囬┈涓殑鎭舵剰浠ｇ爜銆?/p>
            <p>3.鍥剧墖椹<code>.jpg</code>,<code>.png</code>,<code>.gif</code>涓夌鍚庣紑閮戒笂浼犳垚鍔熸墠绠楄繃鍏筹紒</p>
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