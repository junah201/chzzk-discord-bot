"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion, type HTMLMotionProps } from "motion/react";
import Link from "next/link";

const MotionLink = motion.create(Link);

const navLinkVariants = cva(
  "text-foreground/80 hover:text-primary transition-colors relative group",
);

export interface NavLinkProps
  extends Omit<HTMLMotionProps<"a">, "size">,
    VariantProps<typeof navLinkVariants> {
  label: string;
  ref?: React.Ref<HTMLAnchorElement>;
}

const NavLink = ({ className, label, ref, ...props }: NavLinkProps) => {
  return (
    <MotionLink
      {...props}
      ref={ref}
      className={navLinkVariants({ className })}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {label}
      <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300" />
    </MotionLink>
  );
};

export { NavLink, navLinkVariants };
