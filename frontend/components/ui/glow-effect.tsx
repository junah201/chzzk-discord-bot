"use client";

import { motion, type HTMLMotionProps } from "motion/react";
import { cn } from "@/lib/utils";

interface GlowEffectProps extends HTMLMotionProps<"div"> {
  variant?: "static" | "pulse" | "breathing";
  duration?: number; // animation duration in seconds
  delay?: number; // animation delay in seconds
}

const DEFAULT_DURATION = { static: 0, pulse: 4, breathing: 3 } as const;

function getAnimate(
  variant: "static" | "pulse" | "breathing",
  duration: number,
  delay: number,
) {
  switch (variant) {
    case "pulse":
      return {
        opacity: [0.5, 1, 0.5],
        scale: [1, 1.05, 1],
        transition: {
          duration,
          repeat: Infinity,
          ease: "easeInOut" as const,
          delay,
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
  duration,
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
      animate={getAnimate(
        variant,
        duration ?? DEFAULT_DURATION[variant],
        delay,
      )}
      {...props}
    />
  );
};

GlowEffect.displayName = "GlowEffect";

export { GlowEffect };
