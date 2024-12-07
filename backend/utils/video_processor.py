import os
import json
import whisper
import ffmpeg
from datetime import datetime
import logging
from .taiwanese_processor import TaiwaneseProcessor
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from pathlib import Path
from settings import TEMP_FOLDER, PROCESSED_FOLDER

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")
        self.processing_status = {}
        self.taiwanese_processor = TaiwaneseProcessor()

    def process_video(self, video_path, filename):
        """處理影片的主要流程"""
        video_temp_dir = None
        try:
            # 為每個影片建立專屬的存資料夾
            video_temp_dir = TEMP_FOLDER / Path(filename).stem
            if video_temp_dir.exists():
                import shutil
                shutil.rmtree(video_temp_dir)
            video_temp_dir.mkdir(parents=True, exist_ok=True)

            self.processing_status[filename] = {
                'status': 'processing',
                'progress': 0
            }

            # 1. 提取音訊
            audio_path = video_temp_dir / "audio.wav"
            if not self.extract_audio(video_path, str(audio_path)):
                raise Exception("Failed to extract audio")

            self.processing_status[filename]['progress'] = 20

            # 2. 使用 whisper 進行轉錄
            result = self.transcribe_audio(str(audio_path), video_temp_dir)
            if not result:
                raise Exception("Failed to transcribe audio")

            self.processing_status[filename]['progress'] = 40

            # 3. 生成台語語音
            segments = result['segments']
            segment_files = []  # 儲存所有段落的音訊檔案路徑
            
            # 處理每個時間段的文字
            for i, segment in enumerate(segments):
                text = segment['text']
                start_time = segment['start']
                end_time = segment['end']
                
                # 為每個段落生成獨立的音訊檔案
                segment_audio_path = video_temp_dir / f"segment_{i}.wav"
                
                # 轉換為台語並生成語音
                taiwanese_text = self.taiwanese_processor.text_to_taiwanese(text)
                if not taiwanese_text:
                    continue
                    
                if self.taiwanese_processor.synthesize_speech(taiwanese_text, str(segment_audio_path)):
                    segment_files.append({
                        'path': segment_audio_path,
                        'start': start_time,
                        'end': end_time
                    })

            self.processing_status[filename]['progress'] = 60

            # 4. 合成最終影片
            output_filename = Path(filename).stem + '.mp4'
            output_path = PROCESSED_FOLDER / output_filename
            
            if not self.combine_video_segments(video_path, segment_files, str(output_path)):
                raise Exception("Failed to combine video and audio")

            self.processing_status[filename] = {
                'status': 'completed',
                'progress': 100
            }

            # 清理暫存資料夾
            import shutil
            shutil.rmtree(video_temp_dir)

            return output_path

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            self.processing_status[filename] = {
                'status': 'error',
                'progress': 0,
                'error': str(e)
            }
            # 確保清理暫存資料夾
            try:
                if video_temp_dir and video_temp_dir.exists():
                    import shutil
                    shutil.rmtree(video_temp_dir)
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temp directory: {str(cleanup_error)}")
            raise e

    def combine_video_segments(self, video_path, segment_files, output_path):
        """合併影片和多個音訊段落"""
        try:
            logger.info(f"開始合併影片: {video_path}")
            logger.info(f"音訊段落數量: {len(segment_files)}")
            
            from moviepy.editor import (
                VideoFileClip, 
                AudioFileClip, 
                AudioClip,
                CompositeAudioClip,
                CompositeVideoClip,
                afx
            )
            import numpy as np
            from pathlib import Path
            
            # 讀取原始影片
            video = VideoFileClip(video_path)
            
            # 讀取並設置環境音
            ambient_audio_path = Path(__file__).parent.parent / "tools" / "ambient_audio.wav"
            logger.info(f"載入環境音: {ambient_audio_path}")
            
            if ambient_audio_path.exists():
                # 讀取環境音檔案
                ambient_audio = AudioFileClip(str(ambient_audio_path))
                logger.info(f"環境音載入成功，音訊長度: {ambient_audio.duration}秒")
                
                # 計算需要循環的次數
                loop_times = int(np.ceil(video.duration / ambient_audio.duration))
                logger.info(f"需要循環 {loop_times} 次")
                
                # 創建循環的環境音
                ambient_clips = []
                for i in range(loop_times):
                    start_time = i * ambient_audio.duration
                    clip = ambient_audio.copy()
                    clip = clip.set_start(start_time)
                    
                    # 如果是最後一個循環，可能需要裁剪
                    if start_time + ambient_audio.duration > video.duration:
                        clip = clip.subclip(0, video.duration - start_time)
                    
                    # 調整每個環境音片段的音量
                    clip = clip.volumex(2)  # 提高環境音音量到 200%
                    ambient_clips.append(clip)
                    logger.info(f"添加第 {i+1} 環境音片段，開始時間: {start_time}秒")
                
                # 合併所有環境音片段
                ambient_audio = CompositeAudioClip(ambient_clips)
                logger.info(f"環境音合併完成，總長度: {ambient_audio.duration}秒")
            else:
                logger.warning(f"找不到環境音檔案: {ambient_audio_path}")
                ambient_audio = AudioClip(
                    lambda t: np.zeros(2),
                    duration=video.duration
                )
            
            logger.info(f"影片時長: {video.duration}秒")
            
            # 處理配音片段
            audio_clips = []
            for i, segment in enumerate(segment_files):
                try:
                    logger.info(f"處理音訊段落 {i+1}/{len(segment_files)}")
                    audio_path = str(Path(segment['path']).absolute())
                    audio_clip = AudioFileClip(audio_path)
                    
                    # 確保音訊為雙聲道
                    if audio_clip.nchannels == 1:
                        audio_array = audio_clip.to_soundarray()
                        stereo_array = np.column_stack([audio_array, audio_array])
                        audio_clip = AudioClip(
                            lambda t: stereo_array[int(t * audio_clip.fps) % len(stereo_array)],
                            duration=audio_clip.duration
                        )
                    
                    # 調整配音音量
                    audio_clip = audio_clip.volumex(0.8)  
                    
                    duration = segment['end'] - segment['start']
                    logger.info(f"段落時長: {duration}秒")
                    
                    if audio_clip.duration > duration:
                        audio_clip = audio_clip.subclip(0, duration)
                    
                    audio_clip = audio_clip.set_start(segment['start'])
                    audio_clips.append(audio_clip)
                    
                except Exception as e:
                    logger.error(f"處理音訊段落 {i+1} 時發生錯誤: {str(e)}")
                    continue
            
            if not audio_clips:
                raise Exception("沒有有效的音訊段落可以合�")

            logger.info("開始合併音訊...")
            # 合併環境音和配音
            all_audio_clips = [ambient_audio] + audio_clips
            final_audio = CompositeAudioClip(all_audio_clips)
            logger.info(f"音訊合併完成，最終音訊長度: {final_audio.duration}秒")
            
            logger.info("設置影片音訊...")
            final_video = video.set_audio(final_audio)
            
            logger.info("開始輸出影片...")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                audio_bitrate='192k',
                fps=video.fps,
                preset='medium',
                verbose=True,
                threads=4
            )
            
            logger.info("清理資源...")
            video.close()
            final_video.close()
            final_audio.close()
            ambient_audio.close()
            for clip in audio_clips:
                try:
                    clip.close()
                except:
                    pass
            
            logger.info("影片處理完成")
            return True
            
        except Exception as e:
            logger.error(f"合併影片和音訊發生錯誤: {str(e)}")
            # 確保資源被釋放
            try:
                if 'video' in locals():
                    video.close()
                if 'final_video' in locals():
                    final_video.close()
                if 'final_audio' in locals():
                    final_audio.close()
                if 'ambient_audio' in locals():
                    ambient_audio.close()
                if 'audio_clips' in locals():
                    for clip in audio_clips:
                        try:
                            clip.close()
                        except:
                            pass
            except:
                pass
            return False

    def extract_audio(self, video_path, output_path):
        """從影片中提取音訊"""
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar='16k')
            ffmpeg.run(stream, overwrite_output=True)
            return True
        except ffmpeg.Error as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return False

    def transcribe_audio(self, audio_path, video_temp_dir):
        """使用 Whisper 進行語音轉錄"""
        try:
            filename = video_temp_dir.name  # 使用料夾名稱作為檔案名稱
            self.processing_status[filename] = {
                'status': 'transcribing',
                'progress': 0
            }
            
            result = self.model.transcribe(
                audio_path,
                language='zh',
                task='transcribe'
            )

            # 將轉錄結果存放在影片專屬的暫存資料夾中
            transcript_path = video_temp_dir / "transcript.json"
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            self.processing_status[filename]['progress'] = 50
            return result
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            self.processing_status[filename]['status'] = 'error'
            return None

    def get_status(self, filename):
        """獲取處理狀態"""
        return self.processing_status.get(filename, {
            'status': 'unknown',
            'progress': 0
        })