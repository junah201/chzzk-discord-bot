import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import { SnackbarProvider } from 'notistack';
import { ReactNode } from 'react';
import { BrowserRouter } from 'react-router-dom';

import { QueryClient, QueryClientProvider } from '@/lib/Query';
import ThemeProvider from '@/theme';

import 'dayjs/locale/ko';
dayjs.locale('ko');

dayjs.extend(utc);
dayjs.extend(timezone);

const queryClient = new QueryClient();

interface ProvidersProps {
  children: ReactNode;
}

const Providers = ({ children }: ProvidersProps) => {
  return (
    <QueryClientProvider client={queryClient}>
      <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ko">
        <ThemeProvider>
          <SnackbarProvider
            maxSnack={5}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
          >
            <BrowserRouter>{children}</BrowserRouter>
          </SnackbarProvider>
        </ThemeProvider>
      </LocalizationProvider>
    </QueryClientProvider>
  );
};

export default Providers;
