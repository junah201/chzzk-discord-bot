import { ArrowForwardIosOutlined } from '@mui/icons-material';
import {
  Box,
  Avatar,
  Typography,
  Stack,
  useTheme,
  Skeleton,
  IconButton,
} from '@mui/material';
import { Link } from 'react-router-dom';

import { getGuilds, getMe } from '@/api/discord';
import { QUERY } from '@/constants/query';
import { useCustomQuery } from '@/lib';
import { Guild } from '@/types';

const Guilds = () => {
  const theme = useTheme();

  const { data } = useCustomQuery([QUERY.KEY.GUILDS], () => getGuilds(), {});

  const guilds = data?.data;

  if (!guilds) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing(1),
      }}
    >
      {guilds.map((guild) => (
        <GuildBox guild={guild} />
      ))}
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

export default Guilds;
