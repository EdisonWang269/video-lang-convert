import React, { useRef } from 'react';
import { Button, Box } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const VideoUploader = ({ onUploadProgress, onVideoSelect, onStatusChange, onFileNameChange }) => {
  const fileInputRef = useRef();

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 檢查檔案大小 (100MB)
    if (file.size > 100 * 1024 * 1024) {
      alert('檔案大小不能超過 100MB');
      return;
    }

    // 檢查檔案類型
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];
    if (!validTypes.includes(file.type)) {
      alert('請上傳 MP4, MOV 或 AVI 格式的影片');
      return;
    }

    onVideoSelect(URL.createObjectURL(file));
    onStatusChange('uploading');

    const formData = new FormData();
    formData.append('video', file);

    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onUploadProgress(progress);
        },
      });
      
      if (response.data.filename) {
        onFileNameChange(response.data.filename);
        onStatusChange('processing');
      } else {
        throw new Error('No filename returned from server');
      }
    } catch (error) {
      console.error('Upload error:', error);
      onStatusChange('error');
      alert('上傳失敗：' + (error.response?.data?.error || '未知錯誤'));
    }
  };

  return (
    <Box sx={{ textAlign: 'center', my: 3 }}>
      <input
        type="file"
        accept="video/mp4,video/quicktime,video/x-msvideo"
        style={{ display: 'none' }}
        ref={fileInputRef}
        onChange={handleFileSelect}
      />
      <Button
        variant="contained"
        startIcon={<CloudUploadIcon />}
        onClick={() => fileInputRef.current.click()}
      >
        上傳影片
      </Button>
    </Box>
  );
};

export default VideoUploader; 