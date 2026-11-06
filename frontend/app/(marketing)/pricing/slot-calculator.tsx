"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { ArrowDown, ArrowRight, Check, Minus } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import {
  PolicyTable,
  PolicyTbody,
  PolicyTd,
  PolicyTh,
  PolicyThead,
  PolicyTr,
} from "@/components/policy/policy-table";
import routeMap from "@/constants/route-map";
import { cn } from "@/lib/utils";
import { pricingPlans } from "./pricing-plans";
import Reveal from "./reveal";

type Plan = (typeof pricingPlans)[number];

const plans = pricingPlans;
const subscription = plans[plans.length - 1];

// 1~15는 하나씩, 그 뒤로는 듬성듬성 움직이도록 슬라이더 값을 단계로 나눈다
const steps = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 50, 75, 100, 150,
  200, 250,
];
const lastStep = steps.length - 1;
const presets = [3, 5, 10, 15, 50, 250];

const formatPrice = (amount: number) => `₩${amount.toLocaleString("ko-KR")}`;
const stepPercent = (index: number) => (index / lastStep) * 100;

const comparisonRows: {
  label: ReactNode;
  value: (plan: Plan) => ReactNode;
}[] = [
  { label: "결제 방식", value: (plan) => plan.billing },
  {
    label: "알림 슬롯",
    value: (plan) => <span className="tabular-nums">{plan.slots}개</span>,
  },
  { label: "실시간 방송 알림", value: () => true },
  {
    label: (
      <Link
        href={routeMap.DOCS.CUSTOM_WEBHOOK}
        className="underline underline-offset-4 hover:text-primary transition-colors"
      >
        커스텀 웹훅
      </Link>
    ),
    value: (plan) => plan.subscriberFeatures,
  },
  { label: "임베드 색상 변경", value: (plan) => plan.subscriberFeatures },
  {
    label: "고급 필터링",
    value: (plan) =>
      plan.subscriberFeatures && (
        <span className="text-xs text-muted-foreground">지원 예정</span>
      ),
  },
];

function recommendPlan(count: number, needsSubscriberFeatures: boolean): Plan {
  if (needsSubscriberFeatures) return subscription;
  return plans.find((plan) => plan.slots >= count) ?? subscription;
}

function recommendReason(plan: Plan, needsSubscriberFeatures: boolean) {
  if (needsSubscriberFeatures)
    return "커스텀 웹훅과 임베드 색상 변경은 구독한 서버에서만 쓸 수 있습니다.";
  if (plan.id === "free") return "5개까지는 결제 없이 바로 쓸 수 있습니다.";
  if (plan.id === "subscription")
    return "1회 구매로는 15개까지만 늘릴 수 있어서, 그보다 많으면 구독이 필요합니다.";
  return "한 번만 결제하면 늘어난 슬롯을 계속 쓸 수 있습니다.";
}

export default function SlotCalculator() {
  const [stepIndex, setStepIndex] = useState(7);
  const [needsSubscriberFeatures, setNeedsSubscriberFeatures] = useState(false);

  const count = steps[stepIndex];
  const plan = recommendPlan(count, needsSubscriberFeatures);
  const remaining = plan.slots - count;
  const priceLabel = `${formatPrice(plan.amount)}${plan.unit ? ` / ${plan.unit}` : ""}`;

  return (
    <>
      <section
        aria-labelledby="slot-calculator-heading"
        className="grid overflow-hidden rounded-2xl border border-border bg-card lg:grid-cols-[1.35fr_1fr]"
      >
        <h2 id="slot-calculator-heading" className="sr-only">
          요금제 추천
        </h2>
        <p role="status" aria-live="polite" className="sr-only">
          추천 요금제 {plan.name}, {priceLabel}
        </p>

        <div className="border-b border-border p-6 sm:p-10 lg:border-b-0 lg:border-r">
          <label
            htmlFor="slot-count"
            className="text-sm font-medium text-muted-foreground"
          >
            등록할 알림
          </label>
          <p className="mt-3 flex items-baseline gap-3">
            <span className="text-7xl font-bold leading-none tracking-tighter tabular-nums sm:text-8xl">
              {count}
            </span>
            <span className="text-xl text-muted-foreground">개</span>
          </p>
          <p className="mt-3 text-xs text-muted-foreground">
            치지직 채널 하나를 디스코드 채널 한 곳에 보내면 알림 1개입니다.
          </p>

          <div className="mt-10">
            <div className="relative">
              <div className="pointer-events-none absolute inset-x-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-secondary" />
              <div
                className="pointer-events-none absolute left-0 top-1/2 h-1.5 -translate-y-1/2 rounded-full bg-primary"
                style={{ width: `${stepPercent(stepIndex)}%` }}
              />
              <input
                id="slot-count"
                type="range"
                min={0}
                max={lastStep}
                value={stepIndex}
                onChange={(e) => setStepIndex(Number(e.target.value))}
                aria-valuetext={`알림 ${count}개`}
                className={cn(
                  "relative h-7 w-full cursor-pointer appearance-none bg-transparent focus-visible:outline-none",
                  "[&::-webkit-slider-thumb]:size-[22px] [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-4 [&::-webkit-slider-thumb]:border-background [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:shadow-[0_0_0_1px_var(--primary),0_0_24px_rgba(0,229,112,0.45)]",
                  "[&::-moz-range-thumb]:size-3.5 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-4 [&::-moz-range-thumb]:border-background [&::-moz-range-thumb]:bg-primary [&::-moz-range-thumb]:shadow-[0_0_0_1px_var(--primary),0_0_24px_rgba(0,229,112,0.45)]",
                  "focus-visible:[&::-webkit-slider-thumb]:shadow-[0_0_0_3px_var(--primary)]",
                )}
              />
            </div>

            <div className="relative mt-3 h-12" aria-hidden>
              {plans.map((p, i) => {
                const start =
                  i === 0 ? 0 : stepPercent(steps.indexOf(plans[i - 1].slots));
                const end = stepPercent(steps.indexOf(p.slots));
                return (
                  <div
                    key={p.id}
                    className="absolute top-0 h-full border-l border-border pl-2"
                    style={{ left: `${start}%`, width: `${end - start}%` }}
                  >
                    <p
                      className={cn(
                        "truncate text-[11px] font-semibold sm:text-xs",
                        p.id === plan.id
                          ? "text-primary"
                          : "text-muted-foreground",
                      )}
                    >
                      {p.shortName}
                    </p>
                    <p className="mt-0.5 text-[10px] text-muted-foreground/70 tabular-nums sm:text-[11px]">
                      ~{p.slots}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-2">
            {presets.map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => setStepIndex(steps.indexOf(preset))}
                aria-pressed={preset === count}
                className={cn(
                  "cursor-pointer rounded-md border px-3 py-1.5 text-sm tabular-nums transition-colors",
                  preset === count
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:border-foreground/40 hover:text-foreground",
                )}
              >
                {preset}
              </button>
            ))}
          </div>

          <button
            type="button"
            role="switch"
            aria-checked={needsSubscriberFeatures}
            onClick={() => setNeedsSubscriberFeatures((v) => !v)}
            className="mt-8 flex w-full cursor-pointer items-center justify-between gap-4 rounded-xl border border-border bg-background/40 p-4 text-left transition-colors hover:border-foreground/20"
          >
            <span>
              <span className="block text-sm font-medium">
                구독 전용 기능도 필요합니다
              </span>
              <span className="mt-0.5 block text-xs text-muted-foreground">
                커스텀 웹훅으로 알림 보내는 이름과 프로필을, 임베드 색상까지
                바꿀 수 있습니다
              </span>
            </span>
            <span
              className={cn(
                "relative h-6 w-11 shrink-0 rounded-full transition-colors",
                needsSubscriberFeatures ? "bg-primary" : "bg-secondary",
              )}
            >
              <span
                className={cn(
                  "absolute top-1 size-4 rounded-full bg-white transition-all",
                  needsSubscriberFeatures ? "left-6" : "left-1",
                )}
              />
            </span>
          </button>
        </div>

        <div className="flex flex-col p-6 sm:p-10">
          <p className="text-sm font-medium text-muted-foreground">
            추천 요금제
          </p>
          <p className="mt-3 text-3xl font-bold">{plan.name}</p>
          <p className="mt-3 flex items-baseline gap-2">
            <span className="text-5xl font-bold tracking-tight text-primary tabular-nums">
              {formatPrice(plan.amount)}
            </span>
            {plan.unit && (
              <span className="text-muted-foreground">/ {plan.unit}</span>
            )}
          </p>
          <p className="mt-3 min-h-10 text-sm text-muted-foreground">
            {plan.id === "slot-10" ? (
              <>
                1회 구매로는 15개가 최대입니다.{" "}
                <button
                  type="button"
                  onClick={() => setNeedsSubscriberFeatures(true)}
                  className="cursor-pointer text-primary underline underline-offset-4 transition-colors hover:text-primary/80"
                >
                  월 {formatPrice(subscription.amount)} 구독
                </button>
                이면 250개까지 쓸 수 있습니다.
              </>
            ) : (
              recommendReason(plan, needsSubscriberFeatures)
            )}
          </p>

          <div className="mt-5 rounded-xl border border-border p-4">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">슬롯 사용량</span>
              <span className="tabular-nums">
                {count}
                <span className="text-muted-foreground"> / {plan.slots}</span>
              </span>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{
                  width: `${Math.max((count / plan.slots) * 100, 1.5)}%`,
                }}
              />
            </div>
            <p className="mt-3 text-xs text-muted-foreground">
              {remaining === 0
                ? "남는 슬롯 없이 딱 맞습니다."
                : `슬롯이 ${remaining}개 남습니다.`}
            </p>
          </div>

          <ul className="mt-5 mb-6 space-y-2.5 text-sm">
            <li className="flex gap-2">
              <Check className="mt-0.5 size-4 shrink-0 text-primary" />
              알림 슬롯 {plan.slots}개
            </li>
            <li className="flex gap-2">
              <Check className="mt-0.5 size-4 shrink-0 text-primary" />
              실시간 방송 알림
            </li>
            <li
              className={cn(
                "flex gap-2",
                !plan.subscriberFeatures && "text-muted-foreground",
              )}
            >
              {plan.subscriberFeatures ? (
                <Check className="mt-0.5 size-4 shrink-0 text-primary" />
              ) : (
                <Minus className="mt-0.5 size-4 shrink-0" />
              )}
              커스텀 웹훅, 임베드 색상 변경
              {!plan.subscriberFeatures && (
                <span className="text-xs">(구독 전용)</span>
              )}
            </li>
          </ul>

          <LinkButton
            href={plan.amount === 0 ? routeMap.DASHBOARD.HOME : "#payment"}
            className="mt-auto"
          >
            {plan.amount === 0 ? "무료로 시작하기" : "결제 방법 보기"}
            {plan.amount === 0 ? (
              <ArrowRight className="size-4" />
            ) : (
              <ArrowDown className="size-4" />
            )}
          </LinkButton>
        </div>
      </section>

      <Reveal className="mt-20 sm:mt-28">
        <section aria-labelledby="plan-comparison-heading">
          <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <h2
              id="plan-comparison-heading"
              className="text-2xl font-bold tracking-tight sm:text-3xl"
            >
              요금제 비교
            </h2>
            <p className="text-sm text-muted-foreground">
              <span className="mr-1.5 inline-block size-2 rounded-full bg-primary align-middle" />
              알림 {count}개 기준 추천 · 슬롯이 모자란 요금제는 흐리게 표시
            </p>
          </div>

          <PolicyTable className="min-w-[640px]">
            <PolicyThead className="normal-case text-sm">
              <PolicyTh className="sticky left-0 z-10 w-[28%] bg-card shadow-[1px_0_0_var(--border)]">
                <span className="sr-only">항목</span>
              </PolicyTh>
              {plans.map((p) => {
                const short = p.slots < count;
                return (
                  <PolicyTh
                    key={p.id}
                    className={cn(
                      "border-l border-border align-top",
                      p.id === plan.id && "bg-primary/[0.07]",
                    )}
                  >
                    <span
                      className={cn(
                        "block h-0.5 w-6 rounded",
                        p.id === plan.id ? "bg-primary" : "bg-transparent",
                      )}
                    />
                    <span
                      className={cn(
                        "mt-3 block font-semibold",
                        short ? "text-muted-foreground" : "text-foreground",
                      )}
                    >
                      {p.name}
                    </span>
                    <span
                      className={cn(
                        "mt-1 block text-lg font-bold tabular-nums",
                        short ? "text-muted-foreground" : "text-foreground",
                      )}
                    >
                      {formatPrice(p.amount)}
                      {p.unit && (
                        <span className="ml-1 text-xs font-normal text-muted-foreground">
                          / {p.unit}
                        </span>
                      )}
                    </span>
                    {short && <span className="sr-only">(슬롯 부족)</span>}
                  </PolicyTh>
                );
              })}
            </PolicyThead>
            <PolicyTbody>
              {comparisonRows.map((row, index) => (
                <PolicyTr key={index}>
                  <PolicyTd className="sticky left-0 z-10 bg-card text-muted-foreground shadow-[1px_0_0_var(--border)]">
                    {row.label}
                  </PolicyTd>
                  {plans.map((p) => {
                    const value = row.value(p);
                    const short = p.slots < count;
                    return (
                      <PolicyTd
                        key={p.id}
                        className={cn(
                          "border-l border-border",
                          p.id === plan.id && "bg-primary/[0.07]",
                          short && "text-muted-foreground",
                        )}
                      >
                        {value === true ? (
                          <Check
                            className={cn(
                              "size-4",
                              short ? "text-primary/50" : "text-primary",
                            )}
                            aria-label="포함"
                          />
                        ) : value === false ? (
                          <Minus
                            className="size-4 text-muted-foreground/50"
                            aria-label="미포함"
                          />
                        ) : (
                          value
                        )}
                      </PolicyTd>
                    );
                  })}
                </PolicyTr>
              ))}
            </PolicyTbody>
          </PolicyTable>
          <p className="mt-3 text-xs text-muted-foreground">
            1회 구매 슬롯은 기본 5개에 더해집니다. 구독 중에는 슬롯이 250개로
            늘어납니다.
          </p>
        </section>
      </Reveal>
    </>
  );
}
