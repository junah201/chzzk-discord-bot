"use client";

import { useRouter } from "next/navigation";
import routeMap from "@/constants/route-map";
import { useEffect } from "react";
import { getCookie } from "@/lib/cookie";
import { ACCESS_TOKEN } from "@/constants/cookies";

interface AuthGuardProps {
  children: React.ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = () => {
      const token = getCookie(ACCESS_TOKEN.key);

      if (!token) {
        console.log("No access token found, redirecting to login.");
        router.replace(routeMap.AUTH.LOGIN);
      }
    };

    checkAuth();
  }, [router]);

  return <>{children}</>;
}
