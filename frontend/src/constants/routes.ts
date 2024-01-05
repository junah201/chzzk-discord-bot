import { Loadable } from '@/components/Loadable';

export const ROUTES = [
  {
    PATH: '/',
    ELEMENT: Loadable(() => import('@/pages/Home')),
    AUTH: false,
  },
  {
    PATH: '/dashboard',
    ELEMENT: Loadable(() => import('@/pages/Dashboard')),
    AUTH: true,
  },
  {
    PATH: '/login',
    ELEMENT: Loadable(() => import('@/pages/Login')),
    AUTH: false,
  },
  {
    PATH: '/server/:guildId',
    ELEMENT: Loadable(() => import('@/pages/Guild')),
    AUTH: true,
  },
  {
    PATH: '*',
    ELEMENT: Loadable(() => import('@/pages/NotFound')),
    AUTH: false,
  },
];
