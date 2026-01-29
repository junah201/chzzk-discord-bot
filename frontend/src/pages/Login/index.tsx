import { useSnackbar } from 'notistack';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { login } from '@/api/discord';
import { ROUTE } from '@/constants';
import { ACCESS_TOEKN } from '@/constants/cookie';
import { setCookie, getCookie } from '@/lib/Cookie';
const { VITE_DISCORD_CLIENT_ID } = import.meta.env;

const Login = () => {
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();

  const token = getCookie(ACCESS_TOEKN.key);

  if (token) {
    enqueueSnackbar('이미 로그인 되어있습니다.', { variant: 'error' });
    navigate(ROUTE.HOME);
  }

  useEffect(() => {
    // URL에서 authorization code를 추출
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (!code) {
      const url = `https://discord.com/api/oauth2/authorize?client_id=${VITE_DISCORD_CLIENT_ID}&response_type=code&redirect_uri=https%3A%2F%2Fchzzk.junah.dev%2Flogin&scope=identify+email+guilds`;
      window.location.href = url;
      return;
    }

    const getToken = async () => {
      const res = await login(code);

      setCookie(ACCESS_TOEKN.key, res.data.access_token, {
        expires: new Date(Date.now() + res.data.expires_in * 1000),
      });

      navigate(ROUTE.HOME);
    };

    getToken();
  });

  return (
    <>
      <div>로그인 중...</div>
    </>
  );
};

export default Login;
