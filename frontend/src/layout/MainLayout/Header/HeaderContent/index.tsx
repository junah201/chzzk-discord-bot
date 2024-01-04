import { MenuOutlined } from '@mui/icons-material';
import { Box, IconButton, List, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import NavItem from './NavItem';

import LogoSection from '@/components/Logo';

interface HeaderContentProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const HeaderContent = ({ open, setOpen }: HeaderContentProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        width: '100%',
        display: 'flex',
        justifyContent: 'space-between',
      }}
    >
      <LogoSection />
      {!isMobile && (
        <Box
          sx={{
            display: 'flex',
          }}
        >
          <List
            sx={{
              display: 'flex',
              gap: theme.spacing(3),
            }}
          >
            <NavItem name="홈" url="/" />
            <NavItem name="사용법" url="/docs" />
            <NavItem name="서포트 서버" url="https://" />
          </List>
        </Box>
      )}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
        }}
      >
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
