import { Box, Toolbar } from '@mui/material';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';

import Drawer from './Drawer';
import Header from './Header';

const MainLayout = () => {
  const [open, setOpen] = useState(false);

  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
      <Header open={open} setOpen={setOpen} />
      <Drawer open={open} setOpen={setOpen} />
      <Box
        component="main"
        sx={{ width: '100%', flexGrow: 1, p: { xs: 2, sm: 3 } }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;
