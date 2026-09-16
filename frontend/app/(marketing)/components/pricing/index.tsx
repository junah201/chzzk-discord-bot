"use client";

import { motion, useInView } from "motion/react";
import { ArrowRight, Zap } from "lucide-react";
import { useRef } from "react";
import { GlowEffect } from "@/components/ui/glow-effect";
import { LinkButton } from "@/components/ui/link-button";
import routeMap from "@/constants/route-map";
import PricingCard from "../../pricing/pricing-card";
import { pricingPlans } from "../../pricing/pricing-plans";

export function Pricing() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="pricing" className="py-20 sm:py-32 relative overflow-hidden">
      <GlowEffect
        variant="breathing"
        className="top-1/2 left-1/4 w-96 h-96 bg-primary/5"
      />
      <GlowEffect
        variant="breathing"
        delay={2}
        className="bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5"
      />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
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
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6"
          >
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-primary">요금제</span>
          </motion.div>

          <h2 className="text-4xl sm:text-5xl font-bold mb-6">
            <span className="bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
              필요에 딱 맞는
            </span>
            <br />
            <span className="bg-linear-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
              알림 슬롯 요금제
            </span>
          </h2>

          <p className="text-lg text-muted-foreground">
            자유롭게 선택하고 언제든지 변경 가능한 유연한 요금제
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 max-w-7xl mx-auto">
          {pricingPlans.map((plan, index) => (
            <PricingCard key={plan.name} plan={plan} index={index} />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-16"
        >
          <p className="text-muted-foreground mb-6">
            결제 방법과 자세한 이용 안내를 확인해 보세요
          </p>
          <LinkButton
            href={routeMap.PRICING}
            variant="primary"
            effect="glow"
            size="lg"
            className="w-full sm:w-auto"
          >
            요금제 자세히 보기
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </LinkButton>
        </motion.div>
      </div>
    </section>
  );
}
