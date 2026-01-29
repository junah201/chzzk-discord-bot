import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import { ConfirmProvider } from 'material-ui-confirm';
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
            <ConfirmProvider
              defaultOptions={{
                confirmationText: '예',
                cancellationText: '아니요',
                titleProps: {
                  sx: {
                    fontSize: '1rem',
                    fontWeight: 'bold',
                    fontFamily: `'Public Sans', sans-serif`,
                  },
                },
                contentProps: {
                  sx: {
                    fontSize: '0.875rem',
                    fontWeight: 'bold',
                    fontFamily: `'Public Sans', sans-serif`,
                  },
                },
                confirmationButtonProps: {
                  sx: {
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    fontFamily: `'Public Sans', sans-serif`,
                  },
                },
                cancellationButtonProps: {
                  sx: {
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    fontFamily: `'Public Sans', sans-serif`,
                  },
                },
              }}
            >
              <BrowserRouter>{children}</BrowserRouter>
            </ConfirmProvider>
          </SnackbarProvider>
        </ThemeProvider>
      </LocalizationProvider>
    </QueryClientProvider>
  );
};

export default Providers;
