"use client";

import { motion, type HTMLMotionProps } from "motion/react";
import { cn } from "@/lib/utils";

interface GlowEffectProps extends HTMLMotionProps<"div"> {
  variant?: "static" | "pulse" | "breathing";
  duration?: number; // animation duration in seconds
  delay?: number; // animation delay in seconds
}

function getAnimate(
  variant: "static" | "pulse" | "breathing" | undefined,
  duration: number,
  delay: number,
) {
  switch (variant) {
    case "pulse":
      return {
        opacity: [0.5, 1, 0.5],
        scale: [1, 1.05, 1],
        transition: {
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut" as const,
          delay: 0,
        },
      };
    case "breathing":
      return {
        scale: [1, 1.2, 1],
        opacity: [0.4, 0.9, 0.4],
        transition: {
          duration,
          repeat: Infinity,
          ease: "easeInOut" as const,
          delay,
        },
      };
    case "static":
      return {};
    default:
      return {};
  }
}

const GlowEffect = ({
  className,
  variant = "static",
  duration = 3,
  delay = 0,
  ...props
}: GlowEffectProps) => {
  return (
    <motion.div
      className={cn(
        "absolute rounded-full blur-3xl pointer-events-none",
        "bg-primary/10",
        className,
      )}
      initial={variant !== "static" ? { opacity: 0.3, scale: 0.8 } : undefined}
      animate={getAnimate(variant, duration, delay)}
      {...props}
    />
  );
};

GlowEffect.displayName = "GlowEffect";

export { GlowEffect };
