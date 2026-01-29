import { Box, Divider, Drawer } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import DrawerContent from './DrawerContent';
import DrawerFooter from './DrawerFooter';
import DrawerHeader from './DrawerHeader';

import { drawerWidth } from '@/constants/config';

interface DrawerProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const MainDrawer = ({ open, setOpen }: DrawerProps) => {
  const theme = useTheme();

  return (
    <Box
      component="nav"
      sx={{ flexShrink: { md: 0 }, zIndex: 1300 }}
      aria-label="mailbox folders"
    >
      <Drawer
        anchor="right"
        open={open}
        onClose={() => setOpen(false)}
        ModalProps={{
          hideBackdrop: false,
        }}
        sx={{
          display: { xs: 'block', lg: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            borderRight: `1px solid ${theme.palette.divider}`,
            backgroundImage: 'none',
            boxShadow: 'inherit',
          },
        }}
      >
        <DrawerHeader setOpen={setOpen} />
        <Divider flexItem />
        <DrawerContent />
        <Divider flexItem />
        <DrawerFooter />
      </Drawer>
    </Box>
  );
};

export default MainDrawer;
