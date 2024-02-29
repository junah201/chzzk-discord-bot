import {
  Box,
  Link,
  Paper,
  Table,
  TableHead,
  TableRow,
  useTheme,
  TableCell,
  TableBody,
  Typography,
} from '@mui/material';

import DeleteButton from './DeleteButton';
import TestButton from './TestButton';
import ModalButton from './UpdateNoti/ModalButton';

import { getNotificationsByGuildId } from '@/api';
import { QUERY } from '@/constants';
import { useCustomQuery } from '@/lib';
import { Notification } from '@/types';

interface NotiListProps {
  guildId: string;
}

const NotiList = ({ guildId }: NotiListProps) => {
  const theme = useTheme();
  const { data, isLoading, isError } = useCustomQuery(
    [QUERY.KEY.NOTIFICATIONS, { guildId }],
    () => getNotificationsByGuildId(guildId),
    {
      onError: () => {},
      retry: 0,
      cacheTime: 1000 * 60 * 60 * 24,
    }
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
            <TableCell align="center">테스트 알림 전송</TableCell>
            <TableCell align="center">수정</TableCell>
            <TableCell align="center">삭제</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {notificaitons?.map((noti) => (
            <Noti noti={noti} />
          ))}
        </TableBody>
      </Table>
    </Box>
  );
};

interface NotiProps {
  noti: Notification;
}

const Noti = ({ noti }: NotiProps) => {
  const chzzk = noti.PK.replace('CHZZK#', '');

  return (
    <TableRow>
      <TableCell>
        <Link href={`https://chzzk.naver.com/${chzzk}`} target="_blank">
          {chzzk}
        </Link>
      </TableCell>
      <TableCell>
        <Link
          href={`https://discord.com/channels/${noti.guild_id}/${noti.channel_id}`}
          target="_blank"
        >
          #{noti.channel_name}
        </Link>
      </TableCell>
      <TableCell align="center">
        <TestButton chzzk_id={chzzk} channel_id={noti.channel_id} />
      </TableCell>
      <TableCell align="center">
        <ModalButton noti={noti} />
      </TableCell>
      <TableCell align="center">
        <DeleteButton chzzk_id={chzzk} channel_id={noti.channel_id} />
      </TableCell>
    </TableRow>
  );
};

export default NotiList;
