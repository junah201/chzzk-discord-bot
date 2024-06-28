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
    PATH: '/logout',
    ELEMENT: Loadable(() => import('@/pages/Logout')),
    AUTH: false,
  },
  {
    PATH: '/server/:guildId',
    ELEMENT: Loadable(() => import('@/pages/Guild')),
    AUTH: true,
  },
  {
    PATH: '/docs',
    ELEMENT: Loadable(() => import('@/pages/docs/About')),
    AUTH: false,
  },
  {
    PATH: '/docs/about',
    ELEMENT: Loadable(() => import('@/pages/docs/About')),
    AUTH: false,
  },
  {
    PATH: '/docs/chzzk-id',
    ELEMENT: Loadable(() => import('@/pages/docs/ChzzkId')),
    AUTH: false,
  },
  {
    PATH: '/docs/getting-started',
    ELEMENT: Loadable(() => import('@/pages/docs/GettingStarted')),
    AUTH: false,
  },
  {
    PATH: '/docs/mention',
    ELEMENT: Loadable(() => import('@/pages/docs/Mention')),
    AUTH: false,
  },
  {
    PATH: '*',
    ELEMENT: Loadable(() => import('@/pages/NotFound')),
    AUTH: false,
  },
];
