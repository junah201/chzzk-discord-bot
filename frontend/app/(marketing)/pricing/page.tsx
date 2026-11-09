import { GridPattern } from "@/components/ui/grid-pattern";
import { ArrowUpRight } from "lucide-react";
import { Metadata } from "next";
import Link from "next/link";
import CopyButton from "@/components/copy-button";
import routeMap from "@/constants/route-map";
import PricingFaq from "./pricing-faq";
import Reveal from "../components/reveal";
import SlotCalculator from "./slot-calculator";

export const metadata: Metadata = {
  title: "요금제 - 치직",
  description:
    "알림 5개까지는 무료이고, 월 ₩2,000 구독이면 250개까지 쓸 수 있습니다. 필요한 알림 수에 맞는 요금제를 확인하세요.",
  openGraph: {
    title: "요금제 - 치직",
    description:
      "알림 5개까지는 무료입니다. 필요한 알림 수에 맞는 요금제를 확인하세요.",
  },
  twitter: {
    title: "요금제 - 치직",
    description:
      "알림 5개까지는 무료입니다. 필요한 알림 수에 맞는 요금제를 확인하세요.",
  },
};

const ACCOUNT_NUMBER = "09550105001017";

export default function Pricing() {
  return (
    <section className="relative min-h-screen overflow-hidden pt-24 pb-24 break-keep sm:pt-28">
      <GridPattern className="h-[640px]" />

      <div className="container relative z-10 mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <header className="mb-8 max-w-2xl sm:mb-10">
            <p className="mb-5 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              Pricing
            </p>
            <h1 className="text-4xl leading-[1.15] font-bold tracking-tight sm:text-5xl">
              필요한 알림 개수만
              <br />
              정하면 됩니다
            </h1>
            <p className="mt-5 text-lg text-muted-foreground">
              알림이 몇 개 필요한지 고르면 가장 저렴한 요금제를 알려 드립니다.
              5개까지는 무료입니다.
            </p>
          </header>

          <SlotCalculator />

          <Reveal>
            <section
              id="payment"
              aria-labelledby="payment-heading"
              className="mt-20 grid scroll-mt-28 gap-8 border-t border-border pt-12 sm:mt-28 md:grid-cols-[1fr_1.4fr]"
            >
              <div>
                <h2
                  id="payment-heading"
                  className="text-2xl font-bold tracking-tight"
                >
                  결제 방법
                </h2>
                <p className="mt-3 text-sm text-muted-foreground">
                  계좌이체로 결제합니다. 입금한 뒤 서포트 서버에 알려 주시면
                  확인하고 요금제를 적용해 드립니다.
                </p>
              </div>
              <ol className="space-y-3">
                <li className="flex items-center gap-4 rounded-xl border border-border bg-card p-4">
                  <span className="text-sm font-semibold text-primary tabular-nums">
                    01
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs text-muted-foreground">
                      IBK기업은행 · 예금주 김준아
                    </p>
                    <p className="mt-0.5 truncate font-bold tabular-nums">
                      {ACCOUNT_NUMBER}
                    </p>
                  </div>
                  <CopyButton
                    value={ACCOUNT_NUMBER}
                    label="계좌번호 복사"
                    className="shrink-0 gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs hover:border-primary hover:text-primary"
                    iconClassName="size-3.5"
                  >
                    복사
                  </CopyButton>
                </li>
                <li>
                  <Link
                    href={routeMap.REDIRECTS.SUPPORT_SERVER}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center gap-4 rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/50"
                  >
                    <span className="text-sm font-semibold text-primary tabular-nums">
                      02
                    </span>
                    <span className="flex-1 text-sm">
                      서포트 서버에 입금자명, 요금제, 적용할 디스코드 서버를
                      알려 주세요
                    </span>
                    <ArrowUpRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </Link>
                </li>
              </ol>
            </section>
          </Reveal>

          <Reveal className="mt-20 sm:mt-28">
            <PricingFaq />
          </Reveal>
        </div>
      </div>
    </section>
  );
}
