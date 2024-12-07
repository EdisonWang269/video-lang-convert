import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import ReactPlayer from 'react-player';
import './App.css';

function App() {
  const [originalVideo, setOriginalVideo] = useState(null);
  const [processedVideo, setProcessedVideo] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('idle');
  const [currentFilename, setCurrentFilename] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 檢查檔案大小 (100MB)
    if (file.size > 100 * 1024 * 1024) {
      setError('檔案大小不能超過 100MB');
      return;
    }

    // 檢查檔案類型
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];
    if (!validTypes.includes(file.type)) {
      setError('請上傳 MP4, MOV 或 AVI 格式的影片');
      return;
    }

    try {
      // 創建檔案��� URL
      setOriginalVideo(URL.createObjectURL(file));
      setProcessingStatus('uploading');
      setError(null);

      // 準備上傳資料
      const formData = new FormData();
      formData.append('video', file);

      // 上傳檔案
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });
      
      if (response.data.filename) {
        setCurrentFilename(response.data.filename);
        setProcessingStatus('processing');
        setUploadProgress(0); // 重置進度條以顯示處理進度
      } else {
        throw new Error('伺服器未返回檔案名稱');
      }
    } catch (error) {
      console.error('上傳錯誤:', error);
      setProcessingStatus('error');
      setError(error.response?.data?.error || '上傳失敗，請稍後再試');
      // 清理預覽 URL
      if (originalVideo) {
        URL.revokeObjectURL(originalVideo);
        setOriginalVideo(null);
      }
    }
  };

  // 清理函數 - 在組件卸載時清理預覽 URL
  useEffect(() => {
    return () => {
      if (originalVideo) {
        URL.revokeObjectURL(originalVideo);
      }
    };
  }, [originalVideo]);

  // 定期檢查處理狀態
  useEffect(() => {
    let intervalId;

    if (processingStatus === 'processing' && currentFilename) {
      intervalId = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:5000/api/status/${currentFilename}`);
          const { status, progress, error } = response.data;
          
          setProcessingStatus(status);
          setUploadProgress(progress);
          if (error) setError(error);

          if (status === 'completed') {
            setProcessedVideo(`http://localhost:5000/api/result/${currentFilename}`);
            clearInterval(intervalId);
          } else if (status === 'error') {
            clearInterval(intervalId);
          }
        } catch (error) {
          console.error('Status check error:', error);
          setProcessingStatus('error');
          setError('檢查狀態時發生錯誤');
          clearInterval(intervalId);
        }
      }, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [processingStatus, currentFilename]);

  const handleReset = () => {
    setOriginalVideo(null);
    setProcessedVideo(null);
    setUploadProgress(0);
    setProcessingStatus('idle');
    setCurrentFilename(null);
    setError(null);
  };

  return (
    <div className="app-container">
      <div className="cyber-background">
        <div className="cyber-lines"></div>
        <div className="cyber-circles"></div>
        <div className="glow-effect"></div>
      </div>
      
      <motion.div 
        className="content-container"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.h1 
          className="cyber-title"
          initial={{ y: -50 }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 100 }}
        >
          <span className="glow">AI</span> 台語影片轉換
        </motion.h1>

        <div className="main-content">
          <div className="videos-section">
            <motion.div 
              className="video-panel"
              initial={{ x: -100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="panel-header">
                <h3 className="video-title">原始影片</h3>
              </div>
              <div className="player-wrapper">
                {originalVideo ? (
                  <ReactPlayer
                    url={originalVideo}
                    controls
                    width="100%"
                    height="100%"
                    className="react-player"
                  />
                ) : (
                  <motion.div 
                    className="empty-player"
                    whileHover={{ scale: 1.02 }}
                    onClick={() => document.querySelector('.file-input').click()}
                  >
                    <div className="cyber-circle"></div>
                    <p>點擊或拖放影片至此</p>
                    <div className="upload-overlay">
                      <div className="upload-icon"></div>
                      <p>上傳影片</p>
                    </div>
                    <input 
                      type="file" 
                      accept="video/*" 
                      onChange={handleFileChange} 
                      className="file-input"
                      style={{ display: 'none' }}
                    />
                  </motion.div>
                )}
              </div>
            </motion.div>

            <motion.div 
              className="video-panel"
              initial={{ x: 100, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <div className="panel-header">
                <h3 className="video-title">台語配音</h3>
              </div>
              <div className="player-wrapper">
                {processedVideo ? (
                  <ReactPlayer
                    url={processedVideo}
                    controls
                    width="100%"
                    height="100%"
                    className="react-player"
                  />
                ) : (
                  <div className="empty-player">
                    <div className="cyber-circle pulse"></div>
                    <p>{processingStatus === 'processing' ? '處理中...' : '等待處理'}</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          <motion.div 
            className="control-panel"
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div className="status-section">
              {processingStatus === 'processing' && (
                <motion.div 
                  className="processing-status"
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                >
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${uploadProgress}%` }}
                    >
                      <div className="progress-glow"></div>
                    </div>
                  </div>
                  <p className="status-text">處理中... {uploadProgress}%</p>
                </motion.div>
              )}

              {(processingStatus === 'completed' || processingStatus === 'error') && (
                <motion.button
                  className="reset-button"
                  onClick={handleReset}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  重新開始
                </motion.button>
              )}
            </div>

            {error && (
              <motion.div 
                className="error-message"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {error}
              </motion.div>
            )}
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}

export default App;