import {
  Box,
  Avatar,
  Typography,
  Stack,
  Link,
  useTheme,
  Skeleton,
} from '@mui/material';

import { getMe } from '@/api/discord';
import { QUERY } from '@/constants/query';
import { useCustomQuery } from '@/lib';

const Profile = () => {
  const theme = useTheme();

  const { data } = useCustomQuery([QUERY.KEY.ME], () => getMe(), {
    staleTime: Infinity,
    cacheTime: Infinity,
  });

  const user = data?.data;

  if (!user)
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Skeleton variant="circular" width={64} height={64} animation="wave" />
        <Stack
          sx={{
            marginLeft: theme.spacing(2),
            gap: theme.spacing(0.3),
          }}
        >
          <Skeleton width={300} height={35} animation="wave" />
          <Skeleton width={300} height={35} animation="wave" />
        </Stack>
      </Box>
    );

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <Avatar
        alt={user.username}
        src={`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.webp?size=64`}
        sx={{ width: 64, height: 64 }}
      />
      <Stack
        sx={{
          marginLeft: theme.spacing(2),
          gap: theme.spacing(0.1),
        }}
      >
        <Typography variant="h1">{user.global_name}님의 서버 목록</Typography>
        <Typography variant="body1" color={theme.palette.text.secondary}>
          {user.global_name}님이 관리자 권한이 있는 서버만 보여집니다.
        </Typography>
        <Typography variant="body1" color={theme.palette.text.secondary}>
          아래 서버 리스트에서 서버를 골라 관리해보세요.
        </Typography>
        <Typography variant="body1" color={theme.palette.text.secondary}>
          만약 서버가 아래 리스트에 없다면, 이곳을 눌러{' '}
          <Link
            href="https://api.chzzk.junah.dev/invite"
            target="_blank"
            sx={{
              textDecoration: 'underline',
            }}
          >
            치직 봇을 서버에 추가
          </Link>
          해보세요.
        </Typography>
      </Stack>
    </Box>
  );
};

export default Profile;
