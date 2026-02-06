"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion, type HTMLMotionProps } from "motion/react";
import Link from "next/link";

const MotionLink = motion.create(Link);

const navLinkVariants = cva(
  "text-foreground/80 hover:text-primary transition-colors relative group",
);

export interface LogoProps
  extends
    Omit<HTMLMotionProps<"a">, "size">,
    VariantProps<typeof navLinkVariants> {
  label: string;
}

const NavLink = React.forwardRef<HTMLAnchorElement, LogoProps>(
  ({ className, label, ...props }, ref) => {
    return (
      <MotionLink
        {...props}
        className={navLinkVariants({ className })}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {label}
        <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300" />
      </MotionLink>
    );
  },
);

NavLink.displayName = "NavLink";

export { NavLink, navLinkVariants };
