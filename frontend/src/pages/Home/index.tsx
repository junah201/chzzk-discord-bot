import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import Actions from './Actions';
import Intro from './Intro';

const Home = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '80vh',
        width: '100%',
        gap: theme.spacing(2),
        padding: theme.spacing(2),
      }}
    >
      <Intro />
      <Actions />
    </Box>
  );
};

export default Home;
