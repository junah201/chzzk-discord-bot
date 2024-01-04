import { Chip, ListItemButton, ListItemText, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Link } from 'react-router-dom';

import { Menu } from '@/constants/menu';

interface NavItemProps {
  item: Menu;
}

const NavItem = ({ item }: NavItemProps) => {
  const theme = useTheme();

  const textColor = 'text.primary';
  const iconSelectedColor = 'primary.main';
  const isSelected = false;

  return (
    <ListItemButton
      component={Link}
      to={item.url}
      target="_self"
      selected={isSelected}
      sx={{
        zIndex: 1201,
        pl: `28px`,
        py: 0.8,
        '&:hover': {
          bgcolor: 'primary.lighter',
        },
        '&.Mui-selected': {
          bgcolor: 'primary.lighter',
          borderRight: `2px solid ${theme.palette.primary.main}`,
          color: iconSelectedColor,
          '&:hover': {
            color: iconSelectedColor,
            bgcolor: 'primary.lighter',
          },
        },
      }}
    >
      <ListItemText
        primary={
          <Typography
            variant="h3"
            sx={{
              color: isSelected ? iconSelectedColor : textColor,
              fontWeight: 700,
              fontSize: '1rem',
            }}
          >
            {item.title}
          </Typography>
        }
      />
      {item.chip && (
        <Chip
          color={item.chip.color}
          variant={item.chip.variant}
          size={item.chip.size}
          label={item.chip.label}
        />
      )}
    </ListItemButton>
  );
};

export default NavItem;
