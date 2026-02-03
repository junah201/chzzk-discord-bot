"use client";

import { useEffect } from "react";
import { motion } from "motion/react";
import { LogIn, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DISCORD_OAUTH_URL } from "@/constants/links";
import { Loader2 } from "lucide-react";
import { LogoCard } from "@/components/ui/logo-card";

export default function RedirectingToLogin() {
  const handleManualRedirect = () => {
    const isDev = process.env.NODE_ENV === "development";
    if (!isDev) {
      window.location.href = DISCORD_OAUTH_URL;
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      handleManualRedirect();
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Main Content */}
      <div className="relative z-10 w-full max-w-md px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          {/* Pulsing Logo Container */}
          <LogoCard className="mx-auto mb-12" />

          {/* Status Text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mb-8"
          >
            <h1 className="text-3xl sm:text-4xl font-bold mb-4 bg-linear-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
              로그인 중입니다
            </h1>
            <p className="text-lg text-muted-foreground flex items-center justify-center gap-2">
              <LogIn className="w-5 h-5" />
              디스코드 로그인 페이지로 이동 중입니다
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
            <Button
              onClick={handleManualRedirect}
              size="lg"
              className="w-full group"
            >
              <RefreshCw className="w-5 h-5 mr-2 group-hover:rotate-180 transition-transform duration-500" />
              디스코드 로그인하기
            </Button>

            <p className="text-sm text-muted-foreground">
              자동으로 리디렉션되지 않나요?{" "}
              <button
                onClick={handleManualRedirect}
                className="text-primary hover:text-primary/80 underline transition-colors"
              >
                여기를 클릭하세요
              </button>
            </p>
          </motion.div>

          {/* Additional Info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.5 }}
            className="mt-12 pt-8 border-t border-border"
          >
            <div className="bg-card/50 border border-border rounded-xl p-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
                디스코드 계정으로 안전하게 로그인됩니다.
                <br />
                치직은 여러분의 개인정보를 소중히 다룹니다.
              </p>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
