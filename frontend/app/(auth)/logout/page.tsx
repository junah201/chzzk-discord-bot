"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { LogOut, Loader2 } from "lucide-react";

import { LinkButton } from "@/components/ui/link-button";
import { LogoCard } from "@/components/ui/logo-card";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";
import routeMap from "@/constants/route-map";
import { removeCookie } from "@/lib/cookie";
import { ACCESS_TOKEN } from "@/constants/cookies";
import { useAuth } from "@/hooks/use-auth";

export default function LogoutPage() {
  const { logout } = useAuth();

  useEffect(() => {
    const timer = setTimeout(() => {
      logout();
    }, 1000);

    return () => clearTimeout(timer);
  }, [logout]);

  return (
    <StatusPageLayout
      icon={<LogoCard className="mx-auto mb-4" />}
      title="로그아웃 중입니다"
      description={
        <>
          <LogOut className="w-5 h-5 inline" />
          잠시만 기다려주세요
        </>
      }
      footer={
        <div className="bg-card/50 border border-border rounded-xl p-4">
          <p className="text-sm text-muted-foreground leading-relaxed">
            계정 보호를 위해 공용 PC에서는
            <br />
            반드시 브라우저를 종료해주세요.
          </p>
        </div>
      }
    >
      <div className="flex justify-center py-4">
        <Loader2 className="w-16 h-16 text-primary animate-spin" />
      </div>
      <LinkButton
        href={routeMap.HOME}
        variant="secondary"
        size="lg"
        className="w-full group"
      >
        메인으로 돌아가기
      </LinkButton>
      <p className="text-sm text-muted-foreground text-center">
        다시 이용하시려면{" "}
        <Link
          href={routeMap.AUTH.LOGIN}
          className="text-primary hover:text-primary/80 underline transition-colors"
        >
          로그인
        </Link>
        해주세요.
      </p>
    </StatusPageLayout>
  );
}
