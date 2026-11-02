import { useCallback, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { authMutations } from "@/queries/auth";
import { ACCESS_TOKEN } from "@/constants/cookies";
import routeMap from "@/constants/route-map";
import { removeCookie, setCookie } from "@/lib/cookie";
import { sendGAEvent } from "@next/third-parties/google";

const OAUTH_STATE_KEY = "discord-oauth-state";

export const useAuth = () => {
  const router = useRouter();

  const loginWithDiscord = useCallback(() => {
    sendGAEvent("event", "login_attempt");
    const state = crypto.randomUUID();
    sessionStorage.setItem(OAUTH_STATE_KEY, state);
    const url = new URL(process.env.NEXT_PUBLIC_DISCORD_OAUTH_URL as string);
    url.searchParams.set("state", state);
    window.location.href = url.toString();
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

  const { mutate: exchangeCode } = loginMutation;

  const verifySession = useCallback(
    (code: string, state: string | null) => {
      const savedState = sessionStorage.getItem(OAUTH_STATE_KEY);
      sessionStorage.removeItem(OAUTH_STATE_KEY);

      if (!state || state !== savedState) {
        sendGAEvent("event", "exception", {
          description: "oauth_state_mismatch",
        });
        toast.error("로그인 요청을 확인할 수 없습니다. 다시 로그인해 주세요.");
        router.replace(routeMap.AUTH.LOGIN);
        return;
      }

      exchangeCode(code);
    },
    [exchangeCode, router],
  );

  return useMemo(
    () => ({
      redirectToDiscord: loginWithDiscord,
      verifySession,
      logout,
    }),
    [loginWithDiscord, verifySession, logout],
  );
};
