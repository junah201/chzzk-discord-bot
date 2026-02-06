"use client";

import { useEffect } from "react";
import { LogIn, RefreshCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LogoCard } from "@/components/ui/logo-card";
import { useAuth } from "@/hooks/use-auth";
import { StatusPageLayout } from "@/components/layouts/status-page-layout";

export default function RedirectingToLogin() {
  const { redirectToDiscord } = useAuth();

  useEffect(() => {
    const timer = setTimeout(() => redirectToDiscord(), 1000);
    return () => clearTimeout(timer);
  }, [redirectToDiscord]);

  return (
    <StatusPageLayout
      icon={<LogoCard className="mx-auto mb-4" />}
      title="로그인 중입니다"
      description={
        <>
          <LogIn className="w-5 h-5 inline" />
          디스코드 로그인 페이지로 이동 중입니다
        </>
      }
      footer={
        <div className="bg-card/50 border border-border rounded-xl p-4">
          <p className="text-sm text-muted-foreground leading-relaxed">
            디스코드 계정으로 안전하게 로그인됩니다.
            <br />
            치직은 여러분의 개인정보를 소중히 다룹니다.
          </p>
        </div>
      }
    >
      <div className="flex justify-center py-4">
        <Loader2 className="w-16 h-16 text-primary animate-spin" />
      </div>

      <Button onClick={redirectToDiscord} size="lg" className="w-full group">
        <RefreshCw className="w-5 h-5 mr-2 group-hover:rotate-180 transition-transform duration-500" />
        디스코드 로그인하기
      </Button>

      <p className="text-sm text-muted-foreground text-center">
        자동으로 리디렉션되지 않나요?{" "}
        <button
          onClick={redirectToDiscord}
          className="text-primary hover:text-primary/80 underline transition-colors"
        >
          여기를 클릭하세요
        </button>
      </p>
    </StatusPageLayout>
  );
}
