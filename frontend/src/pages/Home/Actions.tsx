import { Button, Box, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Link } from 'react-router-dom';

const Actions = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        gap: theme.spacing(2),
      }}
    >
      <Button
        component="a"
        href="https://api.chzzk.junah.dev/invite"
        target="_blank"
        variant="contained"
        color="primary"
        size="large"
        fullWidth={isMobile}
      >
        서버에 초대하기
      </Button>
      <Button
        component={Link}
        to="/dashboard"
        variant="contained"
        color="inherit"
        size="large"
        fullWidth={isMobile}
      >
        대시보드
      </Button>
    </Box>
  );
};

export default Actions;
