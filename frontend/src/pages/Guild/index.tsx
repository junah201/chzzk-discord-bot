import { Box, useTheme } from '@mui/material';
import { useParams } from 'react-router-dom';

import AddForm from './AddForm';
import NotFound from './NotFound';
import NotiList from './NotiList';

import { getChannels } from '@/api/discord';
import { QUERY } from '@/constants/query';
import { useCustomQuery } from '@/lib';

const GuildDetail = () => {
  const theme = useTheme();
  const params = useParams();
  const { guildId } = params as { guildId: string };

  const { data, isLoading, isError } = useCustomQuery(
    [QUERY.KEY.CHANNELS, { guildId }],
    () => getChannels(guildId),
    {
      onError: () => {},
      retry: 0,
      cacheTime: 1000 * 60 * 60 * 24,
    }
  );

  const channels = data?.data;

  if (isLoading) return null;

  if (isError) return <NotFound></NotFound>;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing(1),
      }}
    >
      <AddForm channels={channels} />
      <NotiList guildId={guildId} />
    </Box>
  );
};

export default GuildDetail;
