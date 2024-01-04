import { Toolbar, AppBar } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';

import HeaderContent from './HeaderContent';

import { drawerWidth } from '@/constants/config';

interface AppBarStyledProps {
  open: boolean;
}

const AppBarStyled = styled(
  AppBar,
  {}
)<AppBarStyledProps>(({ theme, open }) => ({
  backgroundColor: open
    ? theme.palette.background.default
    : theme.palette.background.paper,
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    marginRight: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

interface HeaderProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const Header = ({ open, setOpen }: HeaderProps) => {
  const theme = useTheme();

  return (
    <>
      <AppBarStyled
        open={open}
        position="fixed"
        elevation={0}
        sx={{ borderBottom: `1px solid ${theme.palette.divider}` }}
      >
        <Toolbar>
          <HeaderContent open={open} setOpen={setOpen} />
        </Toolbar>
      </AppBarStyled>
    </>
  );
};

export default Header;
