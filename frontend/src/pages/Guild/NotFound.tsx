import { Box, Typography, useTheme, Button } from '@mui/material';

const NotFound = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: theme.spacing(2),
        height: '100%',
        width: '100%',
      }}
    >
      <Typography
        variant="h1"
        color={theme.palette.text.secondary}
        sx={{
          fontWeight: 'bold',
          fontSize: '10rem',
        }}
      >
        404
      </Typography>
      <Typography
        variant="body1"
        sx={{
          fontSize: '1.5rem',
        }}
      >
        치직 봇이 해당 서버에 없습니다.
      </Typography>
      <Button
        component="a"
        href="https://api.chzzk.junah.dev/invite"
        target="_blank"
        variant="contained"
        color="primary"
        size="large"
      >
        서버에 초대하기
      </Button>
    </Box>
  );
};

export default NotFound;
