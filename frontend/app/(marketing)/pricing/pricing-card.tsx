"use client";

import { motion } from "motion/react";
import { Check } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { pricingPlans } from "./pricing-plans";

interface PricingCardProps {
  plan: (typeof pricingPlans)[number];
  index: number;
}

export default function PricingCard({ plan, index }: PricingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: index * 0.05 }}
      className="relative"
    >
      <Card
        className={cn(
          "h-full gap-0 rounded-2xl p-6 sm:p-8",
          plan.isRecommended && "border-2 border-primary/50",
        )}
      >
        <div className="flex items-center justify-between gap-2">
          <h3 className="text-base font-semibold text-foreground break-keep">
            {plan.name}
          </h3>
          {plan.tag && (
            <span className="shrink-0 rounded-full bg-primary/15 px-2.5 py-0.5 text-xs font-medium text-primary">
              {plan.tag}
            </span>
          )}
        </div>

        <p className="mt-4 flex items-baseline gap-1.5">
          <span className="text-4xl font-bold tracking-tight text-foreground tabular-nums">
            {plan.price}
          </span>
          {plan.unit && (
            <span className="text-sm text-muted-foreground">/ {plan.unit}</span>
          )}
        </p>

        <p className="mt-3 text-sm text-muted-foreground break-keep">
          {plan.description}
        </p>

        <ul className="mt-6 space-y-3 border-t border-border pt-6 text-sm text-muted-foreground">
          {plan.features.map((feature, idx) => (
            <li
              key={idx}
              className={cn(
                "flex items-start gap-2",
                idx === 0 && "font-medium text-foreground",
              )}
            >
              <Check className="mt-0.5 size-4 shrink-0 text-primary" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </Card>
    </motion.div>
  );
}
