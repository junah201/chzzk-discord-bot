"use client";

import { motion } from "motion/react";
import { ArrowRight, BookOpen, Sparkles } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { Logo } from "@/components/ui/logo";
import { GlowEffect } from "@/components/ui/glow-effect";

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
            좋아하는 스트리머의 방송 시작을 디스코드로 실시간 알림받으세요.
            <br className="hidden sm:block" />
            간편한 설정, 빠른 알림, 완벽한 통합.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <LinkButton
              href="#invite"
              variant="primary"
              effect="glow"
              size="lg"
              className="w-full sm:w-auto"
            >
              봇 초대하기
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </LinkButton>
            <LinkButton
              href="#docs"
              variant="secondary"
              size="lg"
              className="w-full sm:w-auto"
            >
              <BookOpen className="w-5 h-5" />
              문서 보기
            </LinkButton>
          </motion.div>

          {/* Floating Cards Animation */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="mt-20 relative"
          >
            <div className="relative max-w-4xl mx-auto">
              {/* Mock Discord Notification */}
              <motion.div
                className="relative bg-linear-to-br from-card to-card/50 backdrop-blur-xl border border-border rounded-2xl p-6 shadow-2xl"
                animate={{
                  y: [0, -10, 0],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <Logo size="sm" showText={false} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold">치직 봇</span>
                      <span className="px-2 py-0.5 bg-primary/20 text-primary text-xs rounded">
                        봇
                      </span>
                      <span className="text-xs text-muted-foreground">
                        방금 전
                      </span>
                    </div>
                    <div className="bg-secondary/50 rounded-lg p-4 border-l-4 border-primary">
                      <p className="text-sm font-semibold mb-1">
                        🔴 방송 시작!
                      </p>
                      <p className="text-sm text-muted-foreground">
                        <span className="text-foreground">스트리머님</span>이
                        방송을 시작했습니다!
                      </p>
                      <div className="mt-3 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                        <span className="text-xs text-muted-foreground">
                          LIVE
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Decorative Elements */}
              <motion.div
                className="absolute -top-4 -right-4 w-24 h-24 bg-primary/20 rounded-full blur-2xl"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.5, 0.3],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
              <motion.div
                className="absolute -bottom-4 -left-4 w-32 h-32 bg-emerald-500/20 rounded-full blur-2xl"
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.3, 0.5, 0.3],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1.5,
                }}
              />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
