import { Box } from '@mui/material';

import Guilds from './Guilds';
import Profile from './Profile';

const Dashboard = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
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
