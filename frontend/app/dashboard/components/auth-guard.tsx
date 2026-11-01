"use client";

import { useRouter } from "next/navigation";
import routeMap from "@/constants/route-map";
import { useEffect, useSyncExternalStore } from "react";
import { getCookie } from "@/lib/cookie";
import { ACCESS_TOKEN } from "@/constants/cookies";

interface AuthGuardProps {
  children: React.ReactNode;
}

const subscribe = () => () => {};
const getHasToken = () => Boolean(getCookie(ACCESS_TOKEN.key));
// 정적 빌드/하이드레이션 중에는 쿠키를 알 수 없으므로 null(확인 전)
const getServerHasToken = () => null;

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const hasToken = useSyncExternalStore(
    subscribe,
    getHasToken,
    getServerHasToken,
  );

  useEffect(() => {
    if (hasToken === false) {
      router.replace(routeMap.AUTH.LOGIN);
    }
  }, [hasToken, router]);

  // 토큰 확인 전에는 children을 렌더링하지 않아, 대시보드 쿼리가 401로 먼저 나가지 않게 함
  if (!hasToken) return null;

  return <>{children}</>;
}
