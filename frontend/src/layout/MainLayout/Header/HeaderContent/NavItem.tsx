import { ListItemButton, ListItemText, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Link } from 'react-router-dom';

interface NavItemProps {
  name: string;
  url: string;
}

const NavItem = ({ name, url }: NavItemProps) => {
  const theme = useTheme();

  return (
    <ListItemButton
      component={Link}
      to={url}
      target="_self"
      sx={{
        '&:hover': {
          bgcolor: 'primary.lighter',
          borderRadius: '99px',
        },
        '&.Mui-selected': {
          bgcolor: 'primary.lighter',
          borderRight: `2px solid ${theme.palette.primary.main}`,
          color: 'primary.main',
          '&:hover': {
            color: 'primary.main',
            bgcolor: 'primary.lighter',
          },
        },
        paddingY: 0,
      }}
    >
      <ListItemText
        primary={
          <Typography
            variant="h3"
            sx={{
              color: 'text.primary',
              fontWeight: 700,
              fontSize: '1rem',
            }}
          >
            {name}
          </Typography>
        }
      />
    </ListItemButton>
  );
};

export default NavItem;
