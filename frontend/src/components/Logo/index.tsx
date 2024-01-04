import { Box, SvgIcon, Typography } from '@mui/material';
import { Link } from 'react-router-dom';

import Logo from './Logo';

const LogoSection = () => {
  return (
    <Box
      component={Link}
      to="/"
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <SvgIcon fontSize="large">
        <Logo />
      </SvgIcon>
      <Typography
        variant="h3"
        sx={{
          paddingLeft: '10px',
        }}
      >
        치직
      </Typography>
    </Box>
  );
};

export default LogoSection;
