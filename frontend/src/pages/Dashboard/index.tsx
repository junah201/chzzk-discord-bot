import { Box, Avatar, Typography, Stack, Link, useTheme } from '@mui/material';

import Guilds from './Guilds';
import Profile from './Profile';

const Dashboard = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        gap: 3,
      }}
    >
      <Profile />
      <Guilds />
    </Box>
  );
};

export default Dashboard;
