"use client";

import { motion, useInView, useSpring, useTransform } from "motion/react";
import { useEffect, useRef } from "react";

const numberFormat = new Intl.NumberFormat("ko-KR");

/** 화면에 들어오면 0부터 value까지 올라가는 숫자 */
export function AnimatedNumber({
  value,
  duration = 2,
}: {
  value: number;
  duration?: number;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  const spring = useSpring(0, {
    bounce: 0,
    duration: duration * 1000,
  });

  const display = useTransform(spring, (current) => {
    if (value >= 100) {
      return numberFormat.format(Math.floor(current));
    }
    return current.toFixed(1);
  });

  useEffect(() => {
    if (isInView) {
      spring.set(value);
    }
  }, [isInView, spring, value]);

  return <motion.span ref={ref}>{display}</motion.span>;
}
