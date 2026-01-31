"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion, type HTMLMotionProps } from "motion/react";
import { Zap } from "lucide-react";
import { cn } from "@/lib/utils";

const logoVariants = cva(
  "inline-flex items-center gap-2 group transition-all",
  {
    variants: {
      size: {
        sm: "gap-1.5",
        md: "gap-2",
        lg: "gap-2.5",
      },
    },
    defaultVariants: {
      size: "md",
    },
  },
);

const iconVariants = cva("text-primary relative", {
  variants: {
    size: {
      sm: "w-6 h-6",
      md: "w-8 h-8",
      lg: "w-10 h-10",
    },
  },
  defaultVariants: {
    size: "md",
  },
});

const textVariants = cva(
  "font-bold bg-gradient-to-r from-primary to-emerald-400 bg-clip-text text-transparent",
  {
    variants: {
      size: {
        sm: "text-lg",
        md: "text-xl",
        lg: "text-2xl",
      },
    },
    defaultVariants: {
      size: "md",
    },
  },
);

export interface LogoProps
  extends
    Omit<HTMLMotionProps<"a">, "size">,
    VariantProps<typeof logoVariants> {
  showText?: boolean;
}

const Logo = React.forwardRef<HTMLAnchorElement, LogoProps>(
  ({ className, size, showText = true, ...props }, ref) => {
    return (
      <motion.a
        ref={ref}
        className={cn(logoVariants({ size, className }))}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        {...props}
      >
        <div className="relative flex items-center justify-center">
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full group-hover:bg-primary/30 transition-all" />
          <Zap className={cn(iconVariants({ size }))} fill="currentColor" />
        </div>
        {showText && <span className={cn(textVariants({ size }))}>치직</span>}
      </motion.a>
    );
  },
);

Logo.displayName = "Logo";

export { Logo, logoVariants };
