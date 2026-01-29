import { List } from '@mui/material';

import NavItem from './NavItem';

import menu from '@/constants/menu';

const NavGroup = () => {
  return (
    <List sx={{ mb: 1, py: 0, zIndex: 0 }}>
      {menu.map((item) => {
        return <NavItem key={item.id} item={item} />;
      })}
    </List>
  );
};

export default NavGroup;
