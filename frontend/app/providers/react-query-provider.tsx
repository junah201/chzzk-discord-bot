"use client";

import {
  QueryClient,
  QueryClientProvider,
  QueryCache,
  MutationCache,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { useState } from "react";
import { isAxiosError } from "axios";
import { ACCESS_TOKEN } from "@/constants/cookies";
import routeMap from "@/constants/route-map";
import { removeCookie } from "@/lib/cookie";
import { getErrorMessage } from "@/lib/api-error";

interface ErrorMeta extends Record<string, unknown> {
  // 화면에서 직접 에러를 보여주는 쿼리/뮤테이션은 전역 토스트를 띄우지 않음
  inlineError?: boolean;
}

declare module "@tanstack/react-query" {
  interface Register {
    queryMeta: ErrorMeta;
    mutationMeta: ErrorMeta;
  }
}

// 여러 쿼리가 동시에 401을 받아도 토스트와 리다이렉트는 한 번만 실행
let isRedirectingToLogin = false;

export default function ReactQueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const handleError = (error: unknown, meta?: ErrorMeta) => {
    if (isAxiosError(error) && error.response?.status === 401) {
      if (isRedirectingToLogin) return;

      toast.error("로그인이 만료되었습니다. 다시 로그인해 주세요.");
      removeCookie(ACCESS_TOKEN.key);

      if (window.location.pathname !== routeMap.AUTH.LOGIN) {
        // 전체 페이지 이동이라 새 페이지에서는 플래그가 다시 false로 시작함
        isRedirectingToLogin = true;
        window.location.href = routeMap.AUTH.LOGIN;
      }
      return;
    }

    if (meta?.inlineError) return;

    toast.error(getErrorMessage(error));
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
          onError: (error, query) => handleError(error, query.meta),
        }),
        mutationCache: new MutationCache({
          onError: (error, _variables, _context, mutation) =>
            handleError(error, mutation.meta),
        }),
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
