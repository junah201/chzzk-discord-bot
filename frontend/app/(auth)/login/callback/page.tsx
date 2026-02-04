"use client";

import { motion } from "motion/react";
import { UserRoundCheck } from "lucide-react";
import { Loader2 } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import routeMap from "@/constants/route-map";
import { LogoCard } from "@/components/ui/logo-card";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Suspense, useEffect } from "react";

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
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="relative z-10 w-full max-w-md px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <LogoCard className="mx-auto mb-12" />

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mb-8"
          >
            <h1 className="text-3xl sm:text-4xl font-bold mb-4 bg-linear-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
              로그인 확인 중입니다
            </h1>
            <p className="text-lg text-muted-foreground flex items-center justify-center gap-2">
              <UserRoundCheck className="w-5 h-5" />
              디스코드에서 정보를 받아오고 있습니다
            </p>
          </motion.div>

          {/* Loading Spinner */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="mb-12 flex justify-center"
          >
            <Loader2 className="w-16 h-16 text-primary animate-spin" />
          </motion.div>

          {/* Fallback Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="space-y-4"
          >
            <LinkButton
              href={routeMap.HOME}
              variant="secondary"
              size="lg"
              className="w-full group border-primary/20 hover:bg-primary/5"
            >
              로그인 취소하기
            </LinkButton>

            <p className="text-sm text-muted-foreground">
              화면이 멈춰있거나 반응이 없나요?{" "}
              <a
                href={routeMap.AUTH.LOGIN}
                className="text-primary hover:text-primary/80 underline transition-colors"
              >
                다시 시도하기
              </a>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="mt-12 pt-8 border-t border-border"
          >
            <div className="bg-card/50 border border-border rounded-xl p-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
                사용자의 정보를 안전하게 검증하고 있습니다.
                <br />
                잠시만 기다려주시면 자동으로 이동합니다.
              </p>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
