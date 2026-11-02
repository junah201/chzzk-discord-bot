"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { ArrowUpRight } from "lucide-react";
import routeMap from "@/constants/route-map";
import PricingCard from "../../pricing/pricing-card";
import { pricingPlans } from "../../pricing/pricing-plans";

export function Pricing() {
  return (
    <section id="pricing" className="relative py-16 sm:py-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="mb-12 flex flex-col gap-6 break-keep md:flex-row md:items-end md:justify-between"
          >
            <div>
              <h2 className="text-4xl leading-[1.15] font-bold tracking-tight sm:text-5xl">
                필요한 만큼만
                <br />
                <span className="text-primary">골라 쓰는 요금제</span>
              </h2>
              <p className="mt-5 max-w-lg text-lg text-muted-foreground">
                알림 5개까지는 무료입니다. 더 필요하면 슬롯을 추가하거나, 정기
                구독으로 250개까지 늘릴 수 있습니다.
              </p>
            </div>
            <Link
              href={routeMap.PRICING}
              className="group inline-flex shrink-0 items-center gap-1.5 self-start border-b border-border pb-1 text-sm font-medium text-foreground/80 transition-colors hover:border-primary hover:text-primary md:self-auto"
            >
              결제 방법과 이용 안내
              <ArrowUpRight className="size-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </Link>
          </motion.div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:gap-8 xl:grid-cols-4">
            {pricingPlans.map((plan, index) => (
              <PricingCard key={plan.name} plan={plan} index={index} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
