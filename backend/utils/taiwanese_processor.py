import os
import json
from datetime import datetime
import requests
import logging
from yating_tts_sdk import YatingClient
from settings import YATING_TTS

logger = logging.getLogger(__name__)

class TaiwaneseProcessor:
    def __init__(self):
        self.processing_status = {}
        self.tts_client = YatingClient(
            YATING_TTS['URL'],
            YATING_TTS['KEY']
        )
        
    def text_to_taiwanese(self, text):
        """將中文文本轉換為台語"""
        try:
            # TODO: 這裡可以加入更複雜的轉換邏輯
            # 目前簡單返回原文
            return text
        except Exception as e:
            logger.error(f"Error converting to Taiwanese: {str(e)}")
            return None

    def synthesize_speech(self, text, output_path):
        """將文本轉換為台語語音"""
        try:
            # 取得檔案名稱（不含副檔名）
            file_name = os.path.splitext(output_path)[0]
            
            # 使用 Yating TTS 進行語音合成
            self.tts_client.synthesize(
                text=text,
                text_type=YatingClient.TYPE_TEXT,
                model=YATING_TTS['DEFAULT_CONFIG']['MODEL'],
                speed=YATING_TTS['DEFAULT_CONFIG']['SPEED'],
                pitch=YATING_TTS['DEFAULT_CONFIG']['PITCH'],
                energy=YATING_TTS['DEFAULT_CONFIG']['ENERGY'],
                encoding=YATING_TTS['DEFAULT_CONFIG']['ENCODING'],
                sample_rate=YATING_TTS['DEFAULT_CONFIG']['SAMPLE_RATE'],
                file_name=file_name
            )
            
            # 檢查生成的檔案是否存在
            generated_file = f"{file_name}.wav"
            if os.path.exists(generated_file):
                # 如果輸出路徑與生成的檔案不同，則進行移動
                if generated_file != output_path:
                    os.rename(generated_file, output_path)
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error synthesizing speech with Yating TTS: {str(e)}")
            return False

    def get_status(self, filename):
        """獲取處理狀態"""
        return self.processing_status.get(filename, {
            'status': 'unknown',
            'progress': 0
        }) 