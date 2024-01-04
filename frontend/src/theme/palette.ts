import { createTheme } from '@mui/material/styles';

export const Palette = () => {
  return createTheme({
    palette: {
      mode: 'dark',
      common: {
        black: '#000',
        white: '#fff',
      },
      primary: {
        main: '#00FFA3',
        dark: '#0A8A5D',
        light: '#00FFA3',
        contrastText: 'rgba(0, 0, 0, 0.87)',
      },
      text: {
        primary: '#dfe2ea',
        secondary: '#c9cedc',
        disabled: '#c9cedc',
      },
      background: {
        paper: '#1E2022',
        default: '#141517',
      },
    },
  });
};

export default Palette;
