import { ThemeOptions } from '../types';

export default function Button(theme: ThemeOptions) {
  const disabledStyle = {
    '&.Mui-disabled': {
      backgroundColor: theme.palette.grey[200],
    },
  };

  return {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          fontWeight: 600,
        },
        contained: {
          ...disabledStyle,
        },
        outlined: {
          ...disabledStyle,
        },
      },
    },
  };
}
