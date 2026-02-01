"use client";

import { motion } from "motion/react";
import { useInView } from "motion/react";
import { useRef } from "react";
import { Bell, Server, TrendingUp, Radio, ArrowRight } from "lucide-react";
import { Metric } from "./metric.interface";
import { MetricCard } from "./metric-card";
import { GlowEffect } from "@/components/ui/glow-effect";
import { LinkButton } from "@/components/ui/link-button";

const metrics: Metric[] = [
  {
    icon: Server,
    value: 14000,
    label: "활성 서버",
    suffix: "+",
    gradient: "from-primary to-emerald-500",
    description: "현재 봇을 사용 중인 디스코드 서버",
  },
  {
    icon: Radio,
    value: 17000,
    label: "모니터링 중인 채널",
    suffix: "+",
    gradient: "from-blue-500 to-cyan-500",
    description: "실시간 감지 중인 치지직 스트리머",
  },
  {
    icon: Bell,
    value: 250,
    label: "누적 알림 전송",
    suffix: "만+",
    gradient: "from-purple-500 to-pink-500",
    description: "유저들에게 전달된 방송 알림 총합",
  },
  {
    icon: TrendingUp,
    value: 99.9,
    label: "가동률",
    suffix: "%",
    gradient: "from-orange-500 to-red-500",
    description: "최근 1년 이상 무사고 운영 중",
  },
];

export function Metrics() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="metrics" className="py-20 sm:py-32 relative overflow-hidden">
      <GlowEffect
        variant="static"
        className="top-1/2 left-0 w-96 h-96 -translate-y-1/2"
      />
      <GlowEffect
        variant="static"
        className="top-1/2 right-0 w-96 h-96 bg-emerald-500/10 -translate-y-1/2"
      />
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={
              isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.5 }
            }
            transition={{ duration: 0.5 }}
            className="inline-block px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6"
          >
            <span className="text-sm font-semibold text-primary">
              신뢰할 수 있는 서비스
            </span>
          </motion.div>

          <h2 className="text-4xl sm:text-5xl font-bold mb-6">
            <span className="bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
              수치로 증명하는
            </span>
            <br />
            <span className="bg-linear-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
              치직의 성장
            </span>
          </h2>

          <p className="text-lg text-muted-foreground">
            많은 사용자들이 선택한 안정적이고 빠른 알림 서비스
          </p>
        </motion.div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 max-w-6xl mx-auto">
          {metrics.map((metric, index) => (
            <MetricCard key={metric.label} metric={metric} index={index} />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-16"
        >
          <p className="text-muted-foreground mb-6">
            지금 바로 치직을 시작하고 커뮤니티에 참여하세요
          </p>
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
        </motion.div>
      </div>
    </section>
  );
}
