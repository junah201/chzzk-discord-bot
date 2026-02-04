"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion, type HTMLMotionProps } from "motion/react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "relative inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 overflow-hidden group",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground",
        secondary:
          "bg-secondary text-secondary-foreground border border-border hover:border-primary/50",
        ghost: "bg-transparent hover:bg-accent text-foreground",
        outline:
          "bg-transparent border border-border hover:bg-muted text-foreground",
      },
      size: {
        default: "px-6 py-2.5 text-base  rounded-lg",
        md: "px-6 py-3 text-base  rounded-xl",
        lg: "px-8 py-4 text-base  rounded-xl",
        icon: "p-2 rounded-lg",
      },
      effect: {
        none: "",
        gradient:
          "before:absolute before:inset-0 before:bg-linear-to-r before:from-primary before:via-emerald-400 before:to-primary before:opacity-0 before:group-hover:opacity-100 before:transition-opacity",
        glow: "",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
      effect: "none",
    },
  },
);

export interface ButtonProps
  extends
    Omit<HTMLMotionProps<"button">, "size" | "children">,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
}

const ButtonInnerContent = ({
  effect,
  children,
}: {
  effect: "none" | "gradient" | "glow" | null | undefined;
  children: React.ReactNode;
}) => (
  <>
    {effect === "glow" && (
      <motion.div
        className="absolute inset-0 bg-primary -z-10"
        initial={false}
        animate={{
          boxShadow: [
            "0 0 15px rgba(0, 229, 112, 0.2)",
            "0 0 30px rgba(0, 229, 112, 0.4)",
            "0 0 15px rgba(0, 229, 112, 0.2)",
          ],
        }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      />
    )}
    <span className="relative z-10 flex w-full min-w-0 items-center justify-center gap-2">
      {children}
    </span>
    {effect === "gradient" && (
      <div className="absolute inset-0 bg-linear-to-r from-emerald-600/20 to-primary/20 opacity-0 group-hover:opacity-100 transition-opacity" />
    )}
  </>
);

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, effect, children, ...props }, ref) => {
    return (
      <motion.button
        className={cn(buttonVariants({ variant, size, effect, className }))}
        ref={ref}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        {...props}
      >
        <ButtonInnerContent effect={effect}>{children}</ButtonInnerContent>
      </motion.button>
    );
  },
);

Button.displayName = "Button";

export { Button, ButtonInnerContent, buttonVariants };
