import { Routes, Route } from 'react-router-dom';

import { ROUTES } from '@/constants/routes';
import MainLayout from '@/layout/MainLayout';

const Router = () => {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        {ROUTES.map(({ PATH, ELEMENT, AUTH }) => (
          <Route key={PATH} path={PATH} element={<ELEMENT />} />
        ))}
      </Route>
    </Routes>
  );
};

export default Router;
