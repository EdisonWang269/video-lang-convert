import React from 'react';
import ReactPlayer from 'react-player';
import { Box } from '@mui/material';

const VideoPlayer = ({ url }) => {
  if (!url) {
    return (
      <Box
        sx={{
          width: '100%',
          height: 200,
          bgcolor: 'grey.200',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        尚未上傳影片
      </Box>
    );
  }

  return (
    <ReactPlayer
      url={url}
      controls
      width="100%"
      height="auto"
      config={{
        file: {
          attributes: {
            controlsList: 'nodownload',
          },
        },
      }}
    />
  );
};

export default VideoPlayer; 