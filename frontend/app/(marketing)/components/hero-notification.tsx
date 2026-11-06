"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useInView } from "motion/react";
import { Bell, Hash, Users } from "lucide-react";
import {
  NotificationPreview,
  NotificationPreviewLive,
} from "@/components/discord/notification-preview";
import { DISCORD_COLORS } from "@/lib/discord";

const DEMO_LIVE: NotificationPreviewLive = {
  channelName: "스트리머",
  title: "오늘은 신작 게임 정주행! 끝까지 갑니다 🎮",
  category: "게임",
  tags: ["한국어", "신작", "정주행"],
};

const TYPING_DURATION_MS = 1600;

/** 히어로의 디스코드 채널 화면. 화면에 들어오면 봇이 입력하다가 알림이 도착하는 순간을 한 번 연출 */
export function HeroNotification() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });
  const [arrived, setArrived] = useState(false);

  useEffect(() => {
    if (!isInView) return;
    const timer = setTimeout(() => setArrived(true), TYPING_DURATION_MS);
    return () => clearTimeout(timer);
  }, [isInView]);

  return (
    <div
      ref={ref}
      className="relative mx-auto max-w-2xl overflow-hidden rounded-xl border border-white/10 text-left shadow-2xl shadow-black/60"
      style={{ backgroundColor: DISCORD_COLORS.bg }}
    >
      <div
        className="flex h-12 items-center gap-2 border-b border-black/30 px-4 shadow-sm"
        style={{ color: DISCORD_COLORS.header }}
      >
        <Hash className="size-5" style={{ color: DISCORD_COLORS.icon }} />
        <span className="font-semibold">방송-알림</span>
        <div
          className="ml-auto flex items-center gap-4"
          style={{ color: DISCORD_COLORS.interactive }}
        >
          <Bell className="size-5" />
          <Users className="size-5" />
        </div>
      </div>

      <div className="flex min-h-[26rem] flex-col justify-end pt-6 pb-2 sm:min-h-[682px]">
        {/* 알림 전의 평범한 대화 */}
        <div
          className="flex gap-4 px-4 py-2 text-[15px] leading-[1.375rem]"
          style={{ color: DISCORD_COLORS.text }}
        >
          <div
            className="mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-full font-semibold text-white"
            style={{ backgroundColor: DISCORD_COLORS.avatar }}
          >
            시
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span
                className="font-medium"
                style={{ color: DISCORD_COLORS.header }}
              >
                시청자
              </span>
              <span className="text-xs" style={{ color: DISCORD_COLORS.muted }}>
                오늘 오후 7:58
              </span>
            </div>
            <p>오늘 방송 언제 켜지려나…</p>
          </div>
        </div>

        <AnimatePresence initial={false}>
          {arrived && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: "spring", stiffness: 260, damping: 26 }}
            >
              <NotificationPreview
                content="@everyone 방송 시작했어요! 놀러 오세요 🎉"
                live={DEMO_LIVE}
                timestampLabel="오늘 오후 8:00"
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* 입력 중 표시 */}
        <div
          className="flex h-6 items-center gap-1.5 px-4 text-xs"
          style={{ color: DISCORD_COLORS.text }}
        >
          {isInView && !arrived && (
            <>
              <span className="flex gap-0.5">
                {[0, 1, 2].map((dot) => (
                  <motion.span
                    key={dot}
                    className="size-1.5 rounded-full"
                    style={{ backgroundColor: DISCORD_COLORS.text }}
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: dot * 0.15,
                    }}
                  />
                ))}
              </span>
              <span>
                <b className="font-semibold">치직</b> 님이 입력하고 있어요...
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
