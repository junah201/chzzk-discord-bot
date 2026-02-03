"use client";

import { motion } from "motion/react";
import { LogOut } from "lucide-react";
import { Loader2 } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import routeMap from "@/constants/route-map";
import { LogoCard } from "@/components/ui/logo-card";

export default function LogoutPage() {
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
              로그아웃 중입니다
            </h1>
            <p className="text-lg text-muted-foreground flex items-center justify-center gap-2">
              <LogOut className="w-5 h-5" />
              잠시만 기다려주세요
            </p>
          </motion.div>

          {/* Loading Spinner or Success Icon */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="mb-12 flex justify-center"
          >
            <Loader2 className="w-16 h-16 text-primary animate-spin" />
          </motion.div>

          {/* Action Buttons */}
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
              className="w-full group"
            >
              메인으로 돌아가기
            </LinkButton>

            <p className="text-sm text-muted-foreground">
              다시 이용하시려면{" "}
              <a
                href={routeMap.AUTH.LOGIN}
                className="text-primary hover:text-primary/80 underline transition-colors"
              >
                로그인
              </a>
              해주세요.
            </p>
          </motion.div>

          {/* Footer Info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="mt-12 pt-8 border-t border-border"
          >
            <div className="bg-card/50 border border-border rounded-xl p-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
                계정 보호를 위해 공용 PC에서는
                <br />
                반드시 브라우저를 종료해주세요.
              </p>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
