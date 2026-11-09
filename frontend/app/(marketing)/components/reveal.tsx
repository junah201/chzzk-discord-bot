"use client";

import { motion, type HTMLMotionProps } from "motion/react";

export const revealProps = (delay = 0) => ({
  initial: { opacity: 0, y: 8 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true },
  transition: { duration: 0.3, delay },
});

interface RevealProps extends HTMLMotionProps<"div"> {
  delay?: number;
}

export default function Reveal({ delay = 0, ...props }: RevealProps) {
  return <motion.div {...revealProps(delay)} {...props} />;
}
