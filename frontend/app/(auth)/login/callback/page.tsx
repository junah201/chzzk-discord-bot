"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { UserRoundCheck, Loader2 } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import routeMap from "@/constants/route-map";

import { LinkButton } from "@/components/ui/link-button";
import { LogoCard } from "@/components/ui/logo-card";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";

export default function LoginCallbackPage() {
  return (
    <Suspense>
      <ClientLoginCallbackPage />
    </Suspense>
  );
}

function ClientLoginCallbackPage() {
  const searchParams = useSearchParams();
  const { verifySession } = useAuth();

  useEffect(() => {
    const code = searchParams.get("code");

    if (code) {
      verifySession(code);
    }
  }, [searchParams, verifySession]);

  return (
    <StatusPageLayout
      icon={<LogoCard className="mx-auto mb-4" />}
      title="로그인 확인 중입니다"
      description={
        <>
          <UserRoundCheck className="w-5 h-5 inline" />
          디스코드에서 정보를 받아오고 있습니다
        </>
      }
      footer={
        <div className="bg-card/50 border border-border rounded-xl p-4">
          <p className="text-sm text-muted-foreground leading-relaxed">
            사용자의 정보를 안전하게 검증하고 있습니다.
            <br />
            잠시만 기다려주시면 자동으로 이동합니다.
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
        className="w-full group border-primary/20 hover:bg-primary/5"
      >
        로그인 취소하기
      </LinkButton>

      <p className="text-sm text-muted-foreground text-center">
        화면이 멈춰있거나 반응이 없나요?{" "}
        <Link
          href={routeMap.AUTH.LOGIN}
          className="text-primary hover:text-primary/80 underline transition-colors"
        >
          다시 시도하기
        </Link>
      </p>
    </StatusPageLayout>
  );
}
