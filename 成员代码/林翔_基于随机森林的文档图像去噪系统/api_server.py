"""文档图像去噪 Web API — 安全加固版"""
import os
import uuid
import pickle
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify

from denoise_config import MODEL_PATH
from helpers import blur_and_threshold

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 上限

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif'}
UPLOAD_DIR = Path(__file__).parent / 'uploads'
OUTPUT_DIR = Path(__file__).parent / 'output'
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ponytail: 简易频率限制，内存字典，重启清空
rate_log = defaultdict(list)
RATE_LIMIT = 20  # 每分钟最多 20 次请求
RATE_WINDOW = timedelta(minutes=1)

print("[INFO] 加载去噪模型...")
model = pickle.load(open(MODEL_PATH, "rb"))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_rate(ip):
    """频率限制检查，超限返回 True"""
    now = datetime.now()
    rate_log[ip] = [t for t in rate_log[ip] if now - t < RATE_WINDOW]
    if len(rate_log[ip]) >= RATE_LIMIT:
        return True
    rate_log[ip].append(now)
    return False


def denoise_image(input_path, output_path):
    """核心去噪逻辑，从 denoise_document.py 抽取"""
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError("无法解码图像")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    orig = gray.copy()

    gray = cv2.copyMakeBorder(gray, 2, 2, 2, 2, cv2.BORDER_REPLICATE)
    gray = blur_and_threshold(gray)

    feats = []
    h, w = gray.shape
    for y in range(h):
        for x in range(w):
            roi = gray[y:y + 5, x:x + 5]
            if roi.shape != (5, 5):
                continue
            feats.append(roi.flatten())

    pixels = model.predict(feats)
    output = (pixels.reshape(orig.shape) * 255).astype("uint8")
    cv2.imwrite(output_path, output)


@app.route('/denoise', methods=['POST'])
def denoise():
    # 频率限制
    ip = request.remote_addr or 'unknown'
    if check_rate(ip):
        return jsonify({"error": "请求过于频繁，请稍后重试"}), 429

    # 文件存在性检查
    if 'file' not in request.files:
        return jsonify({"error": "缺少上传文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400

    # 扩展名白名单
    if not allowed_file(file.filename):
        return jsonify({"error": f"不允许的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    # 文件名清理（防路径穿越）
    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"

    input_path = UPLOAD_DIR / unique_name
    output_name = f"cleaned_{safe_name}"
    output_path = OUTPUT_DIR / output_name

    try:
        file.save(str(input_path))

        # MIME 二次校验
        if not input_path.suffix.lower().lstrip('.') in ALLOWED_EXTENSIONS:
            os.remove(str(input_path))
            return jsonify({"error": "文件扩展名与实际类型不符"}), 400

        denoise_image(str(input_path), str(output_path))
    except ValueError:
        return jsonify({"error": "图像处理失败，请确认文件为有效图像"}), 422
    except Exception:
        return jsonify({"error": "服务内部错误"}), 500
    finally:
        if input_path.exists():
            os.remove(str(input_path))

    return jsonify({
        "status": "ok",
        "output": output_name,
        "message": "去噪完成"
    })


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "文件过大，最大允许 16MB"}), 413


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
