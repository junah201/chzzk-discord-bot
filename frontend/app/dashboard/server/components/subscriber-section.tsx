import Link from "next/link";
import { ArrowRight, Lock } from "lucide-react";

import routeMap from "@/constants/route-map";
import { cn } from "@/lib/utils";

interface SubscriberSectionProps {
  locked: boolean;
  children: React.ReactNode;
}

export default function SubscriberSection({
  locked,
  children,
}: SubscriberSectionProps) {
  return (
    <section
      aria-label="구독자 전용 설정"
      className="overflow-hidden rounded-lg border border-primary/20"
    >
      <div
        className={cn(
          "flex justify-between gap-3 border-b border-primary/15 bg-primary/5 px-4 py-2.5",
          locked ? "items-center" : "items-baseline",
        )}
      >
        <div className="flex items-center gap-2 text-sm font-medium">
          {locked && <Lock className="size-3.5 text-primary" />}
          구독자 전용
          {locked && (
            <span className="hidden font-normal text-muted-foreground sm:inline">
              · 구독하면 사용할 수 있습니다
            </span>
          )}
        </div>
        {locked ? (
          <Link
            href={routeMap.PRICING}
            className="group flex shrink-0 items-center gap-1 text-sm font-medium text-primary hover:text-primary/80"
          >
            요금제 보기
            <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
          </Link>
        ) : (
          <span className="text-xs text-muted-foreground">구독 중</span>
        )}
      </div>
      <div
        className={cn(
          "flex flex-col gap-4 p-4",
          locked && "cursor-not-allowed [&>*]:opacity-75",
        )}
        style={
          locked
            ? {
                backgroundImage:
                  "repeating-linear-gradient(135deg, color-mix(in oklab, var(--primary) 6%, transparent) 0 1px, transparent 1px 10px)",
              }
            : undefined
        }
      >
        {children}
      </div>
    </section>
  );
}
