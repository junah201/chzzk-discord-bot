"use client";

import { motion } from "motion/react";
import { useInView } from "motion/react";
import { useRef } from "react";
import { Zap, Settings, Bell, Shield } from "lucide-react";
import { Feature } from "./feature.interface";
import { FeatureCard } from "./feature-card";
import { GlowEffect } from "@/components/ui/glow-effect";

const features: Feature[] = [
  {
    icon: Zap,
    title: "실시간 알림",
    description:
      "방송 시작과 동시에 디스코드로 즉시 알림을 받아보세요. 단 한 순간도 놓치지 않습니다.",
    gradient: "from-primary to-emerald-500",
  },
  {
    icon: Settings,
    title: "간편한 설정",
    description:
      "복잡한 설정은 이제 그만. 몇 번의 클릭만으로 원하는 스트리머의 알림을 설정할 수 있습니다.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Bell,
    title: "맞춤형 알림",
    description:
      "알림 메시지, 멘션, 채널 등을 자유롭게 커스터마이징하여 서버에 최적화된 알림을 만드세요.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: Shield,
    title: "안정적인 서비스",
    description:
      "24시간 무중단 모니터링으로 언제나 안정적으로 알림을 전송합니다. 신뢰할 수 있는 서비스.",
    gradient: "from-orange-500 to-red-500",
  },
];

export function Features() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="features" className="py-20 sm:py-32 relative overflow-hidden">
      {/* 상단 Primary Glow */}
      <GlowEffect
        variant="breathing" // 원하시면 'static' 또는 'pulse'로 변경 가능
        className="top-1/10 left-1/4 w-96 h-96 bg-primary/5"
      />

      {/* 하단 Emerald Glow */}
      <GlowEffect
        variant="breathing"
        delay={2} // 두 효과가 동시에 움직이지 않도록 딜레이를 주면 더 자연스럽습니다
        className="bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5"
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
              핵심 기능
            </span>
          </motion.div>

          <h2 className="text-4xl sm:text-5xl font-bold mb-6">
            <span className="bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
              치직이 제공하는
            </span>
            <br />
            <span className="bg-linear-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
              강력한 기능들
            </span>
          </h2>

          <p className="text-lg text-muted-foreground">
            스트리머와 시청자를 위한 최고의 알림 서비스
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8 max-w-6xl mx-auto">
          {features.map((feature, index) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}
