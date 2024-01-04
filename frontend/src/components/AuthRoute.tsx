import { useSnackbar } from 'notistack';
import { useState, useEffect } from 'react';
import { Navigate, NavigateProps, RouteProps } from 'react-router-dom';

import { ACCESS_TOEKN } from '@/constants';
import { ROUTE } from '@/constants/route';
import { getCookie } from '@/lib';

export type AuthRouteProps = {
  element: JSX.Element;
  [key: string]: any;
} & RouteProps;

export function AuthRoute({ element, ...rest }: AuthRouteProps) {
  const { enqueueSnackbar } = useSnackbar();
  const [loading, setLoading] = useState(true);
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    const checkValidation = async () => {
      const token = getCookie(ACCESS_TOEKN.key);
      if (!token) {
        enqueueSnackbar('로그인이 필요합니다.', { variant: 'error' });
      } else {
        setIsAuth(!!token);
      }

      setLoading(false);
    };

    checkValidation();
  }, []);

  if (loading) return <>Loading...</>;

  return isAuth ? (
    element
  ) : (
    <Navigate
      to={
        {
          pathname: ROUTE.LOGIN,
          state: { from: rest.location },
        } as NavigateProps['to']
      }
      replace
    />
  );
}
