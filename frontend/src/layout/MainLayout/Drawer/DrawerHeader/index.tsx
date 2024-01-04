import { CloseOutlined } from '@mui/icons-material';
import { Stack, IconButton, Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import DrawerHeaderStyled from './DrawerHeaderStyled';

import Logo from '@/components/Logo';

interface DrawerHeaderProps {
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const DrawerHeader = ({ setOpen }: DrawerHeaderProps) => {
  const theme = useTheme();

  return (
    // only available in paid version
    <DrawerHeaderStyled theme={theme}>
      <Box
        sx={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
        }}
      >
        <Logo />
        <IconButton
          onClick={() => {
            setOpen(false);
          }}
        >
          <CloseOutlined
            sx={{
              color: theme.palette.grey[50],
              fontSize: '2rem',
            }}
          />
        </IconButton>
      </Box>
    </DrawerHeaderStyled>
  );
};

export default DrawerHeader;
