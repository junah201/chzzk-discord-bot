"use client";

import {
  QueryClient,
  QueryClientProvider,
  QueryCache,
  MutationCache,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { useState } from "react";
import Cookies from "js-cookie";
import { isAxiosError } from "axios";
import { ACCESS_TOKEN } from "@/constants/cookies";
import routeMap from "@/constants/route-map";

interface ApiErrorResponse {
  message: string;
}

export default function ReactQueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const handleError = (error: unknown) => {
    if (isAxiosError<ApiErrorResponse>(error)) {
      if (error.response) {
        const { status, data } = error.response;

        if (status === 401) {
          toast.error("세션이 만료되었습니다. 다시 로그인해주세요.");
          Cookies.remove(ACCESS_TOKEN.key);

          if (window.location.pathname !== routeMap.AUTH.LOGIN) {
            window.location.href = routeMap.AUTH.LOGIN;
          }
          return;
        }

        const message = data?.message || "알 수 없는 서버 오류가 발생했습니다.";
        toast.error(message);
        return;
      }

      if (error.request) {
        toast.error("서버와 연결할 수 없습니다. 네트워크를 확인해주세요.");
        return;
      }
    }

    if (error instanceof Error) {
      toast.error(error.message);
      return;
    }

    toast.error("알 수 없는 오류가 발생했습니다.");
  };

  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: (failureCount, error) => {
              if (isAxiosError(error) && error.response?.status === 429) {
                return failureCount < 2;
              }

              return false;
            },
            retryDelay: 500,
            refetchOnWindowFocus: false,
          },
        },
        queryCache: new QueryCache({
          onError: handleError,
        }),
        mutationCache: new MutationCache({
          onError: handleError,
        }),
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
