"use client";

import { ArrowRight, LayoutDashboard } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { GlowEffect } from "@/components/ui/glow-effect";
import routeMap from "@/constants/route-map";
import { HeroNotification } from "./hero-notification";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16 lg:pt-28 lg:pb-12">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <GlowEffect
          variant="pulse"
          className="top-1/4 -left-48 w-96 h-96 bg-primary/10 hidden sm:block"
        />
        <GlowEffect
          variant="pulse"
          delay={2}
          className="bottom-1/4 -right-48 w-96 h-96 bg-emerald-500/10 hidden sm:block"
        />
        <GlowEffect
          variant="static"
          className="top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-150 h-150 bg-primary/5"
        />
      </div>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-5xl mx-auto text-center lg:max-w-7xl lg:grid lg:grid-cols-[minmax(0,5fr)_minmax(0,6fr)] lg:items-center lg:gap-12 lg:text-left xl:gap-16">
          <div>
            <h1 className="text-5xl sm:text-6xl xl:text-7xl font-bold tracking-tight break-keep my-6 leading-tight">
              놓치지 않는
              <br />
              <span className="text-primary">방송 알림, 치직</span>
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed lg:mx-0">
              좋아하는 치지직 스트리머가 방송을 시작하면{" "}
              <br className="hidden sm:block" />
              디스코드 채널로 알려드립니다.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 lg:justify-start">
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
            </div>
          </div>

          <div className="mt-20 lg:mt-0">
            <HeroNotification />
          </div>
        </div>
      </div>
    </section>
  );
}
