import { useState } from "react";
import { useScroll, useMotionValueEvent } from "motion/react";

export function useScrollThreshold(threshold = 10) {
  const [scrolled, setScrolled] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    const isOverThreshold = latest > threshold;
    if (scrolled !== isOverThreshold) {
      setScrolled(isOverThreshold);
    }
  });

  return scrolled;
}
