import React from 'react';
import { Box, LinearProgress, Typography, Alert } from '@mui/material';

const ProcessingStatus = ({ status, progress, error }) => {
  const getStatusMessage = () => {
    switch (status) {
      case 'uploading':
        return '上傳中...';
      case 'transcribing':
        return '正在進行語音辨識...';
      case 'converting':
        return '正在轉換為台語...';
      case 'synthesizing':
        return '正在合成台語語音...';
      case 'merging':
        return '正在合成最終影片...';
      case 'completed':
        return '處理完成';
      case 'error':
        return '處理失敗';
      default:
        return '';
    }
  };

  if (status === 'idle') return null;

  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      {status === 'error' ? (
        <Alert severity="error">
          處理失敗：{error || '未知錯誤'}
        </Alert>
      ) : (
        <>
          <Typography variant="body2" color="text.secondary">
            {getStatusMessage()}
          </Typography>
          {(status !== 'completed') && (
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ mt: 1 }}
            />
          )}
          <Typography variant="body2" color="text.secondary" align="right">
            {progress}%
          </Typography>
        </>
      )}
    </Box>
  );
};

export default ProcessingStatus; 