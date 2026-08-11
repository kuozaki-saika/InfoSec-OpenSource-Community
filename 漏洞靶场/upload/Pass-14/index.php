<?php
include '../config.php';
include '../head.php';
include '../menu.php';
require_once __DIR__ . '/../access_control.php';
check_pass_access('Pass-14');


function getReailFileType($filename){
    $file = fopen($filename, "rb");
    $bin = fread($file, 2); //鍙2瀛楄妭
    fclose($file);
    $strInfo = @unpack("C2chars", $bin);    
    $typeCode = intval($strInfo['chars1'].$strInfo['chars2']);    
    $fileType = '';    
    switch($typeCode){      
        case 255216:            
            $fileType = 'jpg';
            break;
        case 13780:            
            $fileType = 'png';
            break;        
        case 7173:            
            $fileType = 'gif';
            break;
        default:            
            $fileType = 'unknown';
        }    
        return $fileType;
}

$is_upload = false;
$msg = null;
if(isset($_POST['submit'])){
    $temp_file = $_FILES['upload_file']['tmp_name'];
    $file_type = getReailFileType($temp_file);

    if($file_type == 'unknown'){
        $msg = "鏂囦欢鏈煡锛屼笂浼犲け璐ワ紒";
    }else{
        $img_path = UPLOAD_PATH."/".rand(10, 99).date("YmdHis").".".$file_type;
        if(move_uploaded_file($temp_file,$img_path)){
            $is_upload = true;
        } else {
            $msg = "涓婁紶鍑洪敊锛?;
        }
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