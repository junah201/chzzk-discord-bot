import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { GlowEffect } from "@/components/ui/glow-effect";
import { Zap, Bell } from "lucide-react";
import { Metadata } from "next";
import PricingCard from "./pricing-card";
import { pricingPlans } from "./pricing-plans";
import Link from "next/link";
import routeMap from "@/constants/route-map";

export const metadata: Metadata = {
  title: "치직 - 요금제 - 놓치지 않는 방송 알림, 치직",
  description:
    "치직의 간편한 요금제를 확인하고 방송 알림을 시작하세요. 250개 슬롯까지 지원되며, 다양한 기능을 제공합니다.",
  openGraph: {
    title: "치직 - 요금제 - 놓치지 않는 방송 알림, 치직",
    description: "치직의 간편한 요금제를 확인하고 방송 알림을 시작하세요.",
  },
  twitter: {
    title: "치직 - 요금제 - 놓치지 않는 방송 알림, 치직",
    description: "치직의 간편한 요금제를 확인하고 방송 알림을 시작하세요.",
  },
};

export default function Pricing() {
  return (
    <section className="relative min-h-screen pt-32 pb-20 overflow-hidden break-keep">
      {/* Background Effects */}
      <div className="absolute inset-0 pointer-events-none">
        <GlowEffect
          variant="breathing"
          duration={10}
          className="top-0 left-1/4 w-96 h-96 bg-primary/5"
        />
        <GlowEffect
          variant="breathing"
          duration={12}
          delay={2}
          className="bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5"
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center py-20 sm:py-32">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-12">
              <Zap className="w-4 h-4 text-primary" />
              <span className="text-sm text-primary">요금제</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
                필요에 딱 맞는
              </span>
              <br />
              <span className="bg-linear-to-r from-primary via-emerald-400 to-primary bg-clip-text text-transparent">
                알림 슬롯 요금제
              </span>
            </h1>

            <p className="text-lg text-muted-foreground mb-16 max-w-2xl mx-auto">
              자유롭게 선택하고 언제든지 변경 가능한 유연한 요금제로, 스트리머와
              시청자를 위한 최고의 알림 서비스를 경험하세요.
            </p>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
            {pricingPlans.map((plan, index) => (
              <PricingCard key={plan.name} plan={plan} index={index} />
            ))}
          </div>

          {/* Payment Info */}
          <section className="relative py-20 sm:py-32">
            <div className="absolute inset-0 pointer-events-none">
              <GlowEffect
                variant="breathing"
                duration={10}
                className="top-0 left-1/4 w-96 h-96 bg-primary/5"
              />
              <GlowEffect
                variant="breathing"
                duration={12}
                delay={2}
                className="bottom-0 right-1/4 w-96 h-96 bg-emerald-500/5"
              />
            </div>

            <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
              <div className="max-w-2xl mx-auto text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-12">
                  <Bell className="w-4 h-4 text-primary" />
                  <span className="text-sm text-primary">결제 안내</span>
                </div>

                <h2 className="text-3xl sm:text-4xl font-bold mb-8">
                  <span className="bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
                    간편하고 안전한
                  </span>
                  <br />
                  <span className="bg-linear-to-r from-primary via-emerald-400 to-primary bg-clip-text text-transparent">
                    결제 방법
                  </span>
                </h2>

                <div className="bg-card border border-border rounded-xl p-8 space-y-6 text-left">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-primary" />
                      [결제 안내]
                    </h3>
                    <div className="text-sm text-muted-foreground leading-relaxed space-y-2">
                      <div className="flex items-start gap-2">
                        <span className="text-primary shrink-0">•</span>
                        <span>
                          결제 계좌:{" "}
                          <strong className="text-foreground">
                            IBK기업은행 09550105001017
                          </strong>{" "}
                          (예금주: 김준아)
                        </span>
                      </div>
                      <div className="flex items-start gap-2">
                        <span className="text-primary shrink-0">•</span>
                        <span>
                          계좌이체로 진행되며, 입금 후
                          <Link
                            href={routeMap.REDIRECTS.SUPPORT_SERVER}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary underline hover:text-primary/80 transition-colors ml-1"
                          >
                            서포트 서버
                          </Link>
                          에서 말씀해 주세요.
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-12 text-center">
                  <Button
                    variant="primary"
                    size="lg"
                    className="w-full sm:w-auto"
                  >
                    요금제 선택하기
                  </Button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  );
}
