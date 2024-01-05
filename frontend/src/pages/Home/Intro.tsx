import { Grid, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const Intro = () => {
  const theme = useTheme();

  return (
    <>
      <Typography
        variant="h1"
        sx={{
          color: theme.palette.primary.main,
          textAlign: 'center',
          wordBreak: 'keep-all',
        }}
      >
        치지직 커뮤니티를 디스코드에서
      </Typography>
      <Typography
        variant="body1"
        sx={{
          textAlign: 'center',
          wordBreak: 'keep-all',
        }}
      >
        치직 봇을 대시보드와 함께 사용해보세요.
      </Typography>
    </>
  );
};

export default Intro;
