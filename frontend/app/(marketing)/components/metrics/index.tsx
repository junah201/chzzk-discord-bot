"use client";

import { motion } from "motion/react";
import { ArrowRight } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import routeMap from "@/constants/route-map";
import metrics from "@/constants/metrics.json";
import { AnimatedNumber } from "./animated-number";

const secondaryMetrics = [
  { ...metrics.channels, label: "모니터링 중인 치지직 채널" },
  { ...metrics.notifications, label: "누적 방송 알림" },
];

export function Metrics() {
  return (
    <section
      id="metrics"
      className="relative overflow-hidden border-y border-border bg-card/40 py-16 sm:py-24"
    >
      {/* 방송 화면의 주사선 질감 */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0 1px, transparent 1px 4px)",
        }}
      />

      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto grid max-w-6xl items-end gap-12 lg:grid-cols-[minmax(0,7fr)_minmax(0,5fr)]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="break-keep"
          >
            <h2 className="mb-4 text-sm font-semibold text-primary">
              숫자로 보는 치직
            </h2>
            <p className="text-7xl leading-none font-bold tracking-tighter whitespace-nowrap tabular-nums sm:text-8xl lg:text-9xl">
              <AnimatedNumber value={metrics.servers.value} />
              <span className="text-primary">{metrics.servers.suffix}</span>
            </p>
            <p className="mt-5 max-w-md text-lg text-muted-foreground sm:text-xl">
              디스코드 서버가 치직으로 방송 알림을 받고 있습니다.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            <dl className="grid grid-cols-2 divide-x divide-border border-t border-border">
              {secondaryMetrics.map((metric) => (
                <div
                  key={metric.label}
                  className="flex flex-col-reverse pt-6 pr-4 break-keep [&:not(:first-child)]:pl-6"
                >
                  <dt className="mt-2 text-sm text-muted-foreground">
                    {metric.label}
                  </dt>
                  <dd className="text-3xl font-bold tracking-tight whitespace-nowrap tabular-nums sm:text-4xl">
                    <AnimatedNumber value={metric.value} />
                    <span className="text-primary">{metric.suffix}</span>
                  </dd>
                </div>
              ))}
            </dl>

            <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center">
              <LinkButton
                href={routeMap.REDIRECTS.INVITE}
                target="_blank"
                variant="primary"
                size="lg"
                className="w-full sm:w-auto"
              >
                봇 초대하기
                <ArrowRight className="size-5 transition-transform group-hover:translate-x-1" />
              </LinkButton>
              <p className="text-sm text-muted-foreground">
                초대 후 대시보드에서 바로 알림을 등록할 수 있습니다.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
