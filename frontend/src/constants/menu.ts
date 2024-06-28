interface MenuChip {
  color:
    | 'default'
    | 'primary'
    | 'secondary'
    | 'error'
    | 'info'
    | 'success'
    | 'warning';
  variant: 'filled' | 'outlined';
  size: 'small' | 'medium';
  label: string;
}

export interface Menu {
  id: string;
  title: string;
  url: string;
  chip?: MenuChip;
}

const menu: Menu[] = [
  {
    id: 'home',
    title: '홈',
    url: '/',
  },
  {
    id: 'dashboard',
    title: '대시보드',
    url: '/dashboard',
  },
  {
    id: 'about',
    title: '치직 서비스 소개',
    url: '/docs/about',
  },
  {
    id: 'getting-started',
    title: '알림 등록 방법',
    url: '/docs/getting-started',
  },
  {
    id: 'chzzk-id',
    title: '치지직 ID란?',
    url: '/docs/chzzk-id',
  },
  {
    id: 'mention',
    title: '유저 및 역할 멘션하기',
    url: '/docs/mention',
  },
];

export default menu;
