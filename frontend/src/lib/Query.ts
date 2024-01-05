import { AxiosResponse } from 'axios';
import { useSnackbar } from 'notistack';
import { useMutation, useQuery, useQueryClient } from 'react-query';

import { AxiosErr, removeCookie } from '.';

import { ACCESS_TOEKN } from '@/constants';

export { QueryClient, QueryClientProvider } from 'react-query';

interface QueryOptions<DataT> {
  onSuccess?: (res: AxiosResponse<DataT, any>) => void;
  onError?: (error: AxiosErr) => void;
  keepPreviousData?: boolean;
  retry?: number;
  SuccessQueryKey?: any;
  SuccessMessage?: string;
  ErrorMessage?: string;
  staleTime?: number;
  cacheTime?: number;
}

export const useCustomQuery = <DataT = any>(
  queryKey: any[],
  queryFn: () => Promise<AxiosResponse<DataT, any>>,
  options: QueryOptions<DataT>
) => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const query = useQuery(queryKey, queryFn, {
    keepPreviousData: options.keepPreviousData || false,
    retry: options.retry || 1,
    staleTime: options.staleTime || 0,
    cacheTime: options.cacheTime || 5 * 60 * 1000,
    onSuccess: (res) => {
      if (options.SuccessMessage) {
        enqueueSnackbar(options.SuccessMessage, {
          variant: 'success',
        });
      }

      if (options.SuccessQueryKey) {
        queryClient.refetchQueries(options.SuccessQueryKey);
      }

      if (options.onSuccess) {
        options.onSuccess(res);
      }
    },
    onError: (err: AxiosErr) => {
      if (err.response?.status === 401) {
        enqueueSnackbar(`로그인 세션이 만료되었습니다.`, {
          variant: 'error',
        });
        removeCookie(ACCESS_TOEKN.key);
        location.reload();
        return;
      }

      if (options.onError) {
        options.onError(err);
      } else {
        const message =
          options.ErrorMessage || `알 수 없는 에러가 발생했습니다.`;
        const status = err.response?.status ? `${err.response?.status} ` : '';
        const error =
          err.response?.data?.detail || err.message || JSON.stringify(err);

        enqueueSnackbar(`${message} (${status} ${error})`, {
          variant: 'error',
        });
      }
    },
  });

  return {
    ...query,
  };
};

interface MutationOptions {
  onSuccess?: (res: AxiosResponse<any, any>) => void;
  onError?: (error: AxiosErr) => void;
  SuccessMessage?: string;
  SuccessQueryKey?: string | string[];
  ErrorMessage?: string;
}

export const useCustomMutation = <DataT>(
  mutationFn: (userInput: any) => Promise<AxiosResponse<DataT, any>>,
  options: MutationOptions = {}
) => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const mutation = useMutation(mutationFn, {
    onSuccess: (res) => {
      if (options.SuccessMessage) {
        enqueueSnackbar(options.SuccessMessage, {
          variant: 'success',
        });
      }

      if (options.SuccessQueryKey) {
        if (typeof options.SuccessQueryKey === 'string') {
          queryClient.refetchQueries(options.SuccessQueryKey);
        } else if (Array.isArray(options.SuccessQueryKey)) {
          options.SuccessQueryKey.forEach((key) => {
            queryClient.refetchQueries(key);
          });
        }
      }

      if (options.onSuccess) {
        options.onSuccess(res);
      }
    },
    onError: (err: AxiosErr) => {
      if (err.response?.status === 401) {
        enqueueSnackbar(`로그인 세션이 만료되었습니다.`, {
          variant: 'error',
        });
        location.reload();
        return;
      }

      if (options.onError) {
        options.onError(err);
      } else {
        const message =
          options.ErrorMessage || `알 수 없는 에러가 발생했습니다.`;
        const status = err.response?.status ? `${err.response?.status} ` : '';
        const error =
          err.response?.data?.message || err.message || JSON.stringify(err);

        enqueueSnackbar(`${message} (${status} ${error})`, {
          variant: 'error',
        });
      }
    },
  });

  return {
    ...mutation,
  };
};
