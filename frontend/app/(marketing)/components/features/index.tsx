"use client";

import { motion } from "motion/react";
import { Bell, Radio, Zap } from "lucide-react";
import { DISCORD_COLORS } from "@/lib/discord";
import { cn } from "@/lib/utils";

const reveal = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" },
  transition: { duration: 0.5, delay },
});

export function Features() {
  return (
    <section id="features" className="relative py-16 sm:py-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] lg:gap-16">
          <motion.header
            {...reveal()}
            className="break-keep lg:sticky lg:top-32 lg:self-start"
          >
            <p className="mb-5 text-sm font-semibold text-primary">핵심 기능</p>
            <h2 className="text-4xl leading-[1.15] font-bold tracking-tight sm:text-5xl">
              방송 시작을
              <br />
              <span className="text-primary">가장 먼저</span> 알려드립니다
            </h2>
            <p className="mt-6 max-w-md text-lg leading-relaxed text-muted-foreground">
              한 번 설정해 두면, 방송이 시작될 때마다 디스코드 채널로 알림을
              보냅니다.
            </p>
          </motion.header>

          <div className="grid gap-4 sm:grid-cols-2">
            <Tile
              className="sm:col-span-2"
              delay={0}
              title="실시간 알림"
              description="방송이 시작되면 등록한 디스코드 채널로 알림을 보냅니다."
            >
              <SignalFlow />
            </Tile>

            <Tile
              delay={0.08}
              title="간편한 설정"
              description="명령어를 외울 필요 없이, 대시보드에서 클릭 몇 번으로 등록합니다."
            >
              <SetupSteps />
            </Tile>

            <Tile
              delay={0.16}
              title="맞춤형 알림"
              description="알림 메시지, 멘션, 임베드 모양을 서버에 맞게 바꿀 수 있습니다."
            >
              <CustomChips />
            </Tile>

            <Tile
              className="sm:col-span-2"
              delay={0.24}
              title="안정적인 서비스"
              description="24시간 방송 상태를 확인하고, 알림이 잘 전송됐는지 대시보드에서 보여줍니다."
            >
              <UptimeBars />
            </Tile>
          </div>
        </div>
      </div>
    </section>
  );
}

function Tile({
  title,
  description,
  delay,
  className,
  children,
}: {
  title: string;
  description: string;
  delay: number;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <motion.article
      {...reveal(delay)}
      className={cn(
        "flex flex-col gap-6 rounded-2xl border border-border bg-card/60 p-6 sm:p-7",
        className,
      )}
    >
      <div className="flex-1">{children}</div>
      <div className="break-keep">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
      </div>
    </motion.article>
  );
}

/** 방송 시작 → 치직 감지 → 디스코드 도착으로 신호가 흘러가는 그림 */
function SignalFlow() {
  const steps = [
    { icon: Radio, label: "방송 시작", accent: "text-[#ff4d5e]" },
    { icon: Zap, label: "치직 감지", accent: "text-primary" },
    { icon: Bell, label: "디스코드 알림", accent: "text-[#8c9eff]" },
  ];

  return (
    <div className="relative px-2 pt-2">
      {/* 노드를 잇는 선. 화면에 들어오면 왼쪽부터 채워짐 */}
      <div className="absolute top-7 right-[16%] left-[16%] h-px bg-border">
        <motion.div
          className="h-full origin-left bg-linear-to-r from-[#ff4d5e] via-primary to-[#8c9eff]"
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 1.2, ease: "easeInOut", delay: 0.3 }}
        />
      </div>

      <ol className="relative grid grid-cols-3">
        {steps.map(({ icon: Icon, label, accent }) => (
          <li key={label} className="flex flex-col items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-full border border-border bg-background">
              <Icon className={cn("size-[18px]", accent)} />
            </span>
            <span className="text-xs font-medium text-muted-foreground sm:text-sm">
              {label}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

function SetupSteps() {
  const steps = ["봇 초대", "치지직 ID 입력", "알림 채널 선택"];

  return (
    <ol className="flex flex-col gap-2">
      {steps.map((step, index) => (
        <li
          key={step}
          className="flex items-center gap-3 rounded-lg border border-border/70 bg-background/60 px-3 py-2 text-sm"
        >
          <span className="font-mono text-xs text-primary tabular-nums">
            0{index + 1}
          </span>
          {step}
        </li>
      ))}
    </ol>
  );
}

function CustomChips() {
  const chips = [
    { label: "@everyone", mention: true },
    { label: "커스텀 메시지" },
    { label: "임베드 색상" },
    { label: "방송 태그" },
    { label: "바로가기 버튼" },
    { label: "커스텀 웹훅" },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {chips.map(({ label, mention }) => (
        <span
          key={label}
          className={cn(
            "rounded-md px-2.5 py-1 text-sm",
            mention
              ? "font-medium"
              : "border border-border/70 bg-background/60 text-foreground/80",
          )}
          style={
            mention
              ? {
                  backgroundColor: DISCORD_COLORS.mentionBg,
                  color: DISCORD_COLORS.mentionText,
                }
              : undefined
          }
        >
          {label}
        </span>
      ))}
    </div>
  );
}

/** 상태 페이지처럼 하루 단위 막대를 나열한 가동 기록 */
function UptimeBars() {
  const days = 45;

  return (
    <div>
      <div className="mb-3 flex items-baseline justify-between">
        <span className="text-3xl font-bold tracking-tight tabular-nums">
          99.9<span className="text-xl text-muted-foreground">%</span>
        </span>
        <span className="text-xs text-muted-foreground">가동률</span>
      </div>
      <div className="flex h-8 gap-[3px]">
        {Array.from({ length: days }, (_, index) => (
          <motion.span
            key={index}
            className="flex-1 origin-bottom rounded-[2px] bg-primary/80"
            initial={{ scaleY: 0.2, opacity: 0 }}
            whileInView={{ scaleY: 1, opacity: 1 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.3, delay: 0.2 + index * 0.012 }}
          />
        ))}
      </div>
    </div>
  );
}
