import { Box, IconButton, useTheme } from '@mui/material';

import { ReactComponent as Chzzk } from '@/assets/discord.svg';
import { ReactComponent as Github } from '@/assets/github.svg';

const DrawerFooter = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        width: '100%',
        p: theme.spacing(2),
      }}
    >
      <IconButton
        href="https://api.chzzk.junah.dev/support-server"
        target="_blank"
        sx={{
          width: 48,
          height: 48,
        }}
      >
        <Chzzk />
      </IconButton>
      <IconButton
        href="https://github.com/junah201/chzzk-discord-bot"
        target="_blank"
        sx={{
          width: 48,
          height: 48,
        }}
      >
        <Github />
      </IconButton>
    </Box>
  );
};

export default DrawerFooter;
