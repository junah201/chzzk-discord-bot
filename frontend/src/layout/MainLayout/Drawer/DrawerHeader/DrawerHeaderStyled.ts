// material-ui
import { Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const DrawerHeaderStyled = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme }) => ({
  ...theme.mixins.toolbar,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-start',
  paddingLeft: theme.spacing(3),
  paddingRight: theme.spacing(3),
}));

export default DrawerHeaderStyled;
