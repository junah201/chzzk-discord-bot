"use client";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/ui/logo";

interface LogoCardProps {
  className?: string;
  delay?: number;
  duration?: number;
}

export function LogoCard({
  className,
  delay = 0,
  duration = 0.5,
}: LogoCardProps) {
  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay, duration }}
      className={cn("relative inline-block", className)}
    >
      <div className="absolute inset-0 rounded-full bg-primary/20 blur-2xl pointer-events-none" />

      <div className="relative bg-card/50 backdrop-blur-sm border-2 border-primary/20 rounded-2xl p-8 shadow-2xl shadow-primary/10">
        <Logo className="relative z-10" showText={false} size="lg" />
      </div>
    </motion.div>
  );
}
