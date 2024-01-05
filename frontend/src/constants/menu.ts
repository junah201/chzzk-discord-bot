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
];

export default menu;
