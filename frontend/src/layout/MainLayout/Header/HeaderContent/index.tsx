import { MenuOutlined } from '@mui/icons-material';
import { Box, IconButton, List, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';

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
