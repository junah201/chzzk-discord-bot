import {
  Box,
  Link,
  Table,
  TableHead,
  TableRow,
  useTheme,
  TableCell,
  TableBody,
  Typography,
  Tooltip,
} from '@mui/material';
import dayjs from 'dayjs';

import DeleteButton from './DeleteButton';
import TestButton from './TestButton';
import ModalButton from './UpdateNoti/ModalButton';

import { getNotificationsByGuildId } from '@/api';
import { QUERY } from '@/constants';
import { fromNow, useCustomQuery } from '@/lib';
import { Notification } from '@/types';

interface NotiListProps {
  guildId: string;
}

const NotiList = ({ guildId }: NotiListProps) => {
  const theme = useTheme();
  const { data, isLoading } = useCustomQuery(
    [QUERY.KEY.NOTIFICATIONS, { guildId }],
    () => getNotificationsByGuildId(guildId),
    {}
  );

  const notificaitons = data?.data;

  if (isLoading) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: theme.palette.background.paper,
        padding: theme.spacing(3),
        borderRadius: theme.spacing(1),
      }}
    >
      <Typography variant="h4">알림 목록</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>치지직</TableCell>
            <TableCell>디스코드 채널</TableCell>
            <TableCell align="center">마지막 알림</TableCell>
            <TableCell align="center">테스트 알림 전송</TableCell>
            <TableCell align="center">수정</TableCell>
            <TableCell align="center">삭제</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {notificaitons?.map((noti) => (
            <Noti noti={noti} guildId={guildId} />
          ))}
        </TableBody>
      </Table>
    </Box>
  );
};

interface NotiProps {
  noti: Notification;
  guildId: string;
}

const Noti = ({ noti, guildId }: NotiProps) => {
  const chzzk = noti.PK.replace('CHZZK#', '');

  const last_noti_at = noti.last_noti_at
    ? dayjs(noti.last_noti_at).add(9, 'hour').format('YYYY-MM-DD HH:mm:ss')
    : null;

  return (
    <TableRow>
      <TableCell>
        <Typography color="primary.main">
          <Link href={`https://chzzk.naver.com/live/${chzzk}`} target="_blank">
            {chzzk}
          </Link>
        </Typography>
      </TableCell>
      <TableCell>
        <Link
          href={`https://discord.com/channels/${noti.guild_id}/${noti.channel_id}`}
          target="_blank"
        >
          #{noti.channel_name}
        </Link>
      </TableCell>
      {last_noti_at ? (
        <TableCell align="center">
          <Tooltip title={last_noti_at} placement="top">
            <Typography>{fromNow(last_noti_at)}</Typography>
          </Tooltip>
          <Typography
            color={
              noti.last_noti_status === 'SUCCESS'
                ? 'primary.main'
                : 'error.main'
            }
          >
            {noti.last_noti_status}
          </Typography>
        </TableCell>
      ) : (
        <TableCell></TableCell>
      )}
      <TableCell align="center">
        <TestButton
          chzzk_id={chzzk}
          channel_id={noti.channel_id}
          guildId={guildId}
        />
      </TableCell>
      <TableCell align="center">
        <ModalButton noti={noti} guildId={guildId} />
      </TableCell>
      <TableCell align="center">
        <DeleteButton
          guildId={guildId}
          chzzk_id={chzzk}
          channel_id={noti.channel_id}
        />
      </TableCell>
    </TableRow>
  );
};

export default NotiList;
