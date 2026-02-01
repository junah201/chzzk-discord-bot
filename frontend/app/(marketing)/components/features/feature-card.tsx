"use client";

import { useRef } from "react";
import { Feature } from "./feature.interface";
import { motion, useInView } from "motion/react";

interface FeatureCardProps {
  feature: Feature;
  index: number;
}

export const FeatureCard = ({ feature, index }: FeatureCardProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.6, delay: index * 0.1 }}
      className="group relative"
    >
      <div className="relative h-full bg-card border border-border rounded-2xl p-6 sm:p-8 overflow-hidden transition-all duration-300 hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/10">
        {/* Gradient Overlay on Hover */}
        <div className="absolute inset-0 bg-linear-to-br from-primary/0 to-primary/0 group-hover:from-primary/5 group-hover:to-transparent transition-all duration-300" />

        {/* Icon */}
        <motion.div
          className={`relative w-14 h-14 rounded-xl bg-linear-to-br ${feature.gradient} p-3 mb-6`}
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <feature.icon className="w-full h-full text-white" />

          {/* Glow Effect */}
          <motion.div
            className={`absolute inset-0 rounded-xl bg-linear-to-br ${feature.gradient} opacity-0 group-hover:opacity-50 blur-xl transition-opacity`}
          />
        </motion.div>

        {/* Content */}
        <div className="relative">
          <h3 className="text-xl sm:text-2xl font-semibold mb-3 group-hover:text-primary transition-colors">
            {feature.title}
          </h3>
          <p className="text-muted-foreground leading-relaxed break-keepq">
            {feature.description}
          </p>
        </div>

        {/* Decorative Corner */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-linear-to-br from-primary/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
    </motion.div>
  );
};
