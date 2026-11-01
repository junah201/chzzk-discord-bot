import { useCallback, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { authMutations } from "@/queries/auth";
import { ACCESS_TOKEN } from "@/constants/cookies";
import routeMap from "@/constants/route-map";
import { removeCookie, setCookie } from "@/lib/cookie";
import { sendGAEvent } from "@next/third-parties/google";

export const useAuth = () => {
  const router = useRouter();

  const loginWithDiscord = useCallback(() => {
    sendGAEvent("event", "login_attempt");
    window.location.href = process.env.NEXT_PUBLIC_DISCORD_OAUTH_URL as string;
  }, []);

  const loginMutation = useMutation({
    mutationFn: authMutations.login,
    onSuccess: (res) => {
      const expires = new Date(Date.now() + res.expires_in * 1000);

      setCookie(ACCESS_TOKEN.key, res.access_token, {
        expires: expires,
      });

      sendGAEvent("event", "login");

      toast.success("로그인했습니다.");
      router.replace(routeMap.DASHBOARD.HOME);
    },
    onError: (error) => {
      console.error("Login Failed", error);
      sendGAEvent("event", "exception", { description: "login_failed" });
      router.replace(routeMap.AUTH.LOGIN);
    },
  });

  const logout = useCallback(() => {
    removeCookie(ACCESS_TOKEN.key);
    sendGAEvent("event", "logout");
    toast.success("로그아웃했습니다.");
    router.replace(routeMap.HOME);
  }, [router]);

  // useMutation의 mutate는 이미 안정적인 참조이므로 그대로 사용한다
  const verifySession = loginMutation.mutate;

  return useMemo(
    () => ({
      redirectToDiscord: loginWithDiscord,
      verifySession,
      logout,
    }),
    [loginWithDiscord, verifySession, logout],
  );
};
