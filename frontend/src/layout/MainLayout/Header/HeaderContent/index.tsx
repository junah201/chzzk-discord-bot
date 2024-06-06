import { MenuOutlined } from '@mui/icons-material';
import { Box, Button, IconButton, List, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Link } from 'react-router-dom';

import LogoSection from '@/components/Logo';
import { ACCESS_TOEKN, ROUTE } from '@/constants';
import { getCookie } from '@/lib';

interface HeaderContentProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const HeaderContent = ({ open, setOpen }: HeaderContentProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const isLogin = getCookie(ACCESS_TOEKN.key);

  return (
    <Box
      sx={{
        width: '100%',
        display: 'flex',
        justifyContent: 'space-between',
      }}
    >
      <LogoSection />
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
        }}
      >
        {isLogin ? (
          <>
            <Link to={ROUTE.LOGOUT}>
              <Button color="inherit">Logout</Button>
            </Link>
          </>
        ) : (
          <Link to={ROUTE.LOGIN}>
            <Button color="inherit">Login</Button>
          </Link>
        )}
        {!open && !isMobile ? (
          <IconButton onClick={() => setOpen((prev) => !prev)}>
            <MenuOutlined />
          </IconButton>
        ) : null}
      </Box>
    </Box>
  );
};

export default HeaderContent;
