import { Outlet } from 'react-router-dom';

import RouteChangeTracker from '@/lib/ReactGA4';

const MinimalLayout = () => {
  RouteChangeTracker();

  return <Outlet />;
};

export default MinimalLayout;
