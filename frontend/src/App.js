import React, { useState, useEffect } from 'react';
import { Box, Container, Paper, Typography, LinearProgress, Button } from '@mui/material';
import VideoUploader from './components/VideoUploader';
import VideoPlayer from './components/VideoPlayer';
import ProcessingStatus from './components/ProcessingStatus';
import './App.css';
import axios from 'axios';

function App() {
  const [originalVideo, setOriginalVideo] = useState(null);
  const [processedVideo, setProcessedVideo] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('idle');
  const [currentFilename, setCurrentFilename] = useState(null);
  const [error, setError] = useState(null);

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
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          中文影片轉台語系統
        </Typography>
        
        <VideoUploader 
          onUploadProgress={setUploadProgress}
          onVideoSelect={setOriginalVideo}
          onStatusChange={setProcessingStatus}
          onFileNameChange={setCurrentFilename}
        />

        <ProcessingStatus 
          status={processingStatus} 
          progress={uploadProgress}
          error={error}
        />

        <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="h6" gutterBottom>
              原始影片
            </Typography>
            <VideoPlayer url={originalVideo} />
          </Paper>

          <Paper sx={{ flex: 1, p: 2 }}>
            <Typography variant="h6" gutterBottom>
              處理後影片
            </Typography>
            <VideoPlayer url={processedVideo} />
          </Paper>
        </Box>

        {(processingStatus === 'completed' || processingStatus === 'error') && (
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleReset}
            >
              重新開始
            </Button>
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default App;
