import { ArrowForwardIosOutlined, LaunchOutlined } from '@mui/icons-material';
import {
  Box,
  Avatar,
  Typography,
  useTheme,
  IconButton,
  useMediaQuery,
} from '@mui/material';
import { Link } from 'react-router-dom';

import { getGuilds } from '@/api/discord';
import Adfit from '@/components/Adfit';
import { QUERY } from '@/constants/query';
import { useCustomQuery } from '@/lib';
import { Guild } from '@/types';

const Guilds = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width: 1024px)');

  const { data } = useCustomQuery([QUERY.KEY.GUILDS], () => getGuilds(), {});

  const guilds = data?.data;

  if (!guilds) return null;

  const units = ['DAN-WdpYAzcPE5hZQTG9', 'DAN-nnsaHluduZYQ4HQ6'];

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing(1),
      }}
    >
      {guilds.map((guild, index) => (
        <>
          <GuildBox guild={guild} />
          {(index + 1) % 5 == 0 && isMobile && (
            <Adfit
              unit={units[Math.floor(Math.random() * units.length)]}
              width={320}
              height={50}
            />
          )}
        </>
      ))}
      <SupportServer />
    </Box>
  );
};

interface GuildProps {
  guild: Guild;
}

const GuildBox = ({ guild }: GuildProps) => {
  const theme = useTheme();

  return (
    <Box
      component={Link}
      to={`/server/${guild.id}`}
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: theme.spacing(1),
        backgroundColor: theme.palette.background.paper,
        padding: theme.spacing(2),
        borderRadius: theme.spacing(2),
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing(1),
        }}
      >
        <Avatar
          alt={guild.name}
          src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.webp?size=64`}
          sx={{ width: 64, height: 64 }}
        />
        <Typography variant="h4">{guild.name}</Typography>
      </Box>
      <IconButton>
        <ArrowForwardIosOutlined />
      </IconButton>
    </Box>
  );
};

const SupportServer = () => {
  const theme = useTheme();

  return (
    <Box
      component="a"
      href="https://api.chzzk.junah.dev/support-server"
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: theme.spacing(1),
        backgroundColor: '#5865F2',

        paddingX: theme.spacing(2),
        paddingY: theme.spacing(1),
        borderRadius: theme.spacing(2),
        marginTop: theme.spacing(2),
      }}
    >
      <Typography variant="h5">
        도움이 필요하십니까? 서포트 디스코드 서버에 참여하세요.
      </Typography>
      <IconButton>
        <LaunchOutlined />
      </IconButton>
    </Box>
  );
};

export default Guilds;
