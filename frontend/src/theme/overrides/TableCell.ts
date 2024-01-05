import { ThemeOptions } from '../types';

export default function TableCell(theme: ThemeOptions) {
  return {
    MuiTableCell: {
      styleOverrides: {
        root: {
          fontSize: '0.875rem',
          padding: 8,
          borderColor: theme.palette.divider,
        },
        head: {
          fontWeight: 600,
          paddingTop: 12,
          paddingBottom: 12,
        },
      },
    },
  };
}
