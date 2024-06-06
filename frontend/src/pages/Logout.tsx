import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';

import { ROUTE, ACCESS_TOEKN } from '@/constants';
import { removeCookie } from '@/lib/Cookie';

const Logout = () => {
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    removeCookie(ACCESS_TOEKN.key);
    window.location.href = ROUTE.HOME;

    setIsLoading(false);
  }, []);

  return isLoading ? <>Logout...</> : <Navigate to={ROUTE.HOME} />;
};

export default Logout;
