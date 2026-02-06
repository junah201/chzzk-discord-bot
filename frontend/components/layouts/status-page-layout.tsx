"use client";

import { motion } from "motion/react";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatusPageLayoutProps {
  icon: ReactNode;
  title: string;
  description?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
}

export function StatusPageLayout({
  icon,
  title,
  description,
  children,
  footer,
  className,
}: StatusPageLayoutProps) {
  return (
    <div
      className={cn(
        "min-h-screen flex items-center justify-center p-4 relative overflow-hidden",
        className,
      )}
    >
      <div className="max-w-md w-full text-center space-y-8 relative z-10">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            type: "spring",
            stiffness: 200,
            damping: 20,
            delay: 0.1,
          }}
          className="relative inline-block"
        >
          {icon}
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="space-y-4"
        >
          <h1 className="text-3xl sm:text-4xl font-bold bg-linear-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent">
            {title}
          </h1>
          {description && (
            <div className="text-lg text-muted-foreground leading-relaxed flex items-center justify-center gap-2">
              {description}
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className="space-y-4 flex flex-col"
        >
          {children}
        </motion.div>

        {footer && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="pt-6 border-t border-border/50"
          >
            {footer}
          </motion.div>
        )}
      </div>
    </div>
  );
}
