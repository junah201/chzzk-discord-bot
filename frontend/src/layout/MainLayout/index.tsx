import { Box, useMediaQuery } from '@mui/material';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';

import Drawer from './Drawer';
import Header from './Header';

import Adfit from '@/components/Adfit';
import RouteChangeTracker from '@/lib/ReactGA4';

const MainLayout = () => {
  const [open, setOpen] = useState(false);
  const isMobile = useMediaQuery('(max-width: 1024px)');

  RouteChangeTracker();

  return (
    <Box sx={{ display: 'flex', width: '100%', minHeight: '100vh' }}>
      <Header open={open} setOpen={setOpen} />
      <Drawer open={open} setOpen={setOpen} />
      <Box
        component="main"
        display="flex"
        sx={{
          width: '100%',
          flexGrow: 1,
          marginTop: '60px',
          p: { xs: 2, sm: 2 },
        }}
        justifyContent="space-between"
      >
        {!isMobile && (
          <Box width={160} height={600}>
            <Adfit unit="DAN-lKBAcWcRabtfqMJV" width={160} height={600} />
          </Box>
        )}
        <Outlet />
        {!isMobile && (
          <Box width={160} height={600}>
            <Adfit unit="DAN-LL8I5qPhrj6DEaZm" width={160} height={600} />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default MainLayout;
