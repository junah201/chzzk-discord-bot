import { Box, IconButton, useTheme } from '@mui/material';

import { ReactComponent as Chzzk } from '@/assets/discord.svg';
import { ReactComponent as Github } from '@/assets/github.svg';
import { ROUTE } from '@/constants';

const DrawerFooter = () => {
  const theme = useTheme();

  return (
    <Box>
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
          rel="nofollow"
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
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          width: '100%',
          gap: theme.spacing(2),
        }}
      >
        <Box
          component="a"
          href={ROUTE.TERMS}
          sx={{
            fontSize: theme.typography.body2.fontSize,
            color: theme.palette.text.secondary,
            textDecoration: 'none',
          }}
        >
          서비스 이용약관
        </Box>
        <Box
          component="a"
          href={ROUTE.PRIVACY}
          sx={{
            fontSize: theme.typography.body2.fontSize,
            color: theme.palette.text.secondary,
            textDecoration: 'none',
          }}
        >
          개인정보 처리방침
        </Box>
      </Box>
    </Box>
  );
};

export default DrawerFooter;
