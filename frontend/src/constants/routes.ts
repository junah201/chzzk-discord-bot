import { Loadable } from '@/components/Loadable';

export const ROUTES = [
  {
    PATH: '/',
    ELEMENT: Loadable(() => import('@/pages/Home')),
    AUTH: false,
  },
  {
    PATH: '/login',
    ELEMENT: Loadable(() => import('@/pages/Login')),
    AUTH: false,
  },
];
