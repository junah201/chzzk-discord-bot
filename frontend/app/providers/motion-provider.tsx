"use client";

import { MotionConfig } from "motion/react";

// OS의 "동작 줄이기" 설정을 켠 사용자에게는 이동/확대 애니메이션을 끔
export default function MotionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
