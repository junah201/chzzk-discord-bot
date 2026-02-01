"use client";

import { motion, useInView, useSpring, useTransform } from "motion/react";
import { Metric } from "./metric.interface";
import { useEffect, useRef } from "react";

function AnimatedNumber({
  value,
  duration = 2,
}: {
  value: number;
  duration?: number;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  const spring = useSpring(0, {
    bounce: 0,
    duration: duration * 1000,
  });

  const display = useTransform(spring, (current) => {
    if (value >= 100) {
      return Math.floor(current).toLocaleString();
    }
    return current.toFixed(1);
  });

  useEffect(() => {
    if (isInView) {
      spring.set(value);
    }
  }, [isInView, spring, value]);

  return <motion.span ref={ref}>{display}</motion.span>;
}

interface MetricCardProps {
  metric: Metric;
  index: number;
}

export const MetricCard = ({ metric, index }: MetricCardProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={isInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="group relative"
    >
      <div className="relative bg-card border border-border rounded-2xl p-8 overflow-hidden transition-all duration-300 hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/10">
        {/* Background Gradient */}
        <div
          className={`absolute inset-0 bg-linear-to-br ${metric.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}
        />

        {/* Icon */}
        <motion.div
          className={`relative w-12 h-12 rounded-xl bg-linear-to-br ${metric.gradient} p-2.5 mb-6 mx-auto`}
          whileHover={{ scale: 1.1, rotate: 10 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <metric.icon className="w-full h-full text-white" />

          {/* Glow Effect */}
          <motion.div
            className={`absolute inset-0 rounded-xl bg-linear-to-br ${metric.gradient} blur-xl opacity-0 group-hover:opacity-50 transition-opacity`}
          />
        </motion.div>

        {/* Value */}
        <div className="relative text-center">
          <div className="text-4xl sm:text-5xl font-bold mb-2 bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
            <AnimatedNumber value={metric.value} />
            {metric.suffix}
          </div>
          <p className="text-muted-foreground font-medium">{metric.label}</p>
        </div>

        {/* Decorative Elements */}
        <div className="absolute -top-10 -right-10 w-32 h-32 bg-linear-to-br from-primary/10 to-transparent rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
        <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-linear-to-br from-emerald-500/10 to-transparent rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500" />
      </div>
    </motion.div>
  );
};
