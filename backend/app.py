from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import logging
from utils.video_processor import VideoProcessor
import threading
from settings import UPLOAD_FOLDER, PROCESSED_FOLDER, TEMP_FOLDER
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 設定上傳檔案的相關配置
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

video_processor = VideoProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER / filename
            file.save(str(filepath))
            
            # 在背景執行影片處理
            def process():
                try:
                    video_processor.process_video(str(filepath), filename)
                except Exception as e:
                    logger.error(f"Error processing video: {str(e)}")

            threading.Thread(target=process).start()
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename
            }), 200
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/status/<filename>')
def get_status(filename):
    status = video_processor.get_status(filename)
    return jsonify(status)

@app.route('/api/result/<filename>')
def get_result(filename):
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        return send_file(file_path)
    except Exception as e:
        logger.error(f"Error sending result file: {str(e)}")
        return jsonify({'error': 'File not found'}), 404

# 在應用程式啟動時確保目錄存在
def ensure_directories():
    for directory in [UPLOAD_FOLDER, PROCESSED_FOLDER, TEMP_FOLDER]:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    ensure_directories()
    app.run(host='0.0.0.0', port=5000) 