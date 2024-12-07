import os
from pathlib import Path
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 建立基礎路徑
BASE_DIR = Path(__file__).resolve().parent

# 基本設定
DEBUG = True
SECRET_KEY = 'your-secret-key-here'

# 檔案上傳相關設定
UPLOAD_FOLDER = BASE_DIR / 'uploads'
PROCESSED_FOLDER = BASE_DIR / 'processed' 
TEMP_FOLDER = BASE_DIR / 'temp'

# 確保必要的資料夾存在
UPLOAD_FOLDER.mkdir(exist_ok=True)
PROCESSED_FOLDER.mkdir(exist_ok=True)
TEMP_FOLDER.mkdir(exist_ok=True)

# Yating TTS 設定
YATING_TTS = {
    'URL': os.getenv('YATING_TTS_URL'),
    'KEY': os.getenv('YATING_TTS_KEY'),
    'DEFAULT_CONFIG': {
        'MODEL': 'tai_female_2',  # 使用台語女聲
        'SPEED': 0.75,
        'PITCH': 1.3,
        'ENERGY': 1.5,
        'ENCODING': 'LINEAR16',
        'SAMPLE_RATE': '16K'
    }
}

# 日誌設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'app.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
} 