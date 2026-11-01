"use client";

import { motion } from "motion/react";
import { ArrowRight, LayoutDashboard, Sparkles } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { GlowEffect } from "@/components/ui/glow-effect";
import routeMap from "@/constants/route-map";
import { HeroNotification } from "./hero-notification";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* 왼쪽 위: Pulse 효과 */}
        <GlowEffect
          variant="pulse"
          className="top-1/4 -left-48 w-96 h-96 bg-primary/10 hidden sm:block"
        />
        {/* 오른쪽 아래: Pulse 효과 + 딜레이 */}
        <GlowEffect
          variant="pulse"
          delay={2}
          className="bottom-1/4 -right-48 w-96 h-96 bg-emerald-500/10 hidden sm:block"
        />
        {/* 중앙: 정적(Static) 배경 */}
        <GlowEffect
          variant="static"
          className="top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-150 h-150 bg-primary/5"
        />
      </div>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8"
          >
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-primary">
              치지직 스트리밍 알림 봇
            </span>
          </motion.div>

          {/* Main Heading */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight"
          >
            <span className="bg-linear-to-r from-foreground via-foreground to-foreground/60 bg-clip-text text-transparent">
              놓치지 않는
            </span>
            <br />
            <span className="bg-linear-to-r from-primary via-emerald-400 to-primary bg-clip-text text-transparent">
              방송 알림, 치직
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg sm:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed"
          >
            좋아하는 치지직 스트리머가 방송을 시작하면{" "}
            <br className="hidden sm:block" />
            디스코드 채널로 알려드립니다.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <LinkButton
              href={routeMap.REDIRECTS.INVITE}
              target="_blank"
              variant="primary"
              effect="glow"
              size="lg"
              className="w-full sm:w-auto"
            >
              봇 초대하기
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </LinkButton>
            <LinkButton
              href={routeMap.DASHBOARD.HOME}
              variant="secondary"
              size="lg"
              className="w-full sm:w-auto"
            >
              <LayoutDashboard className="w-5 h-5" />
              대시보드
            </LinkButton>
          </motion.div>

          {/* Notification Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mt-20"
          >
            <HeroNotification />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
