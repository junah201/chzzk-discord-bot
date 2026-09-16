"use client";

import { motion } from "motion/react";
import { Check, Crown, Shield, Star, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { pricingPlans } from "./pricing-plans";

const planIcons = {
  crown: Crown,
  shield: Shield,
  star: Star,
  zap: Zap,
} as const;

interface PricingCardProps {
  plan: (typeof pricingPlans)[number];
  index: number;
}

export default function PricingCard({ plan, index }: PricingCardProps) {
  const PlanIcon = planIcons[plan.icon];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: index * 0.05 }}
      className="group relative"
    >
      <Card
        className={cn(
          "h-full bg-card border border-border rounded-2xl p-6 sm:p-8",
          "transition-all duration-300",
          "hover:border-primary/50 hover:shadow-2xl hover:shadow-primary/10",
          plan.isRecommended && "border-2 border-primary/50",
        )}
      >
        {/* Badge */}
        {plan.badge && (
          <div className="mb-4 flex items-center gap-2 flex-wrap">
            <Badge
              variant="outline"
              className={cn(
                "text-xs font-medium px-3 py-1",
                plan.isRecommended || plan.isPopular
                  ? "border-primary/50 text-primary"
                  : "border-border/50 text-muted-foreground",
              )}
            >
              {plan.badge}
            </Badge>
            {plan.isPopular && (
              <span className="text-xs bg-primary/20 text-primary rounded-full px-2 py-0.5">
                인기
              </span>
            )}
            {plan.isRecommended && (
              <span className="text-xs bg-primary/20 text-primary rounded-full px-2 py-0.5">
                추천
              </span>
            )}
          </div>
        )}

        {/* Icon */}
        <div className="relative w-16 h-16 rounded-xl mb-6">
          <div
            className={`absolute inset-0 rounded-xl bg-linear-to-br ${plan.color} p-2.5`}
          >
            <PlanIcon className="w-full h-full text-white" />
          </div>
          {/* Glow effect on hover */}
          <motion.div
            className={cn(
              `absolute inset-0 rounded-xl bg-linear-to-br ${plan.color}`,
              "opacity-0 group-hover:opacity-50 blur-xl transition-opacity",
            )}
          />
        </div>

        {/* Plan Info */}
        <CardHeader className="px-0 pt-0 pb-4">
          <CardTitle className="text-2xl font-bold text-foreground mb-2">
            {plan.name}
          </CardTitle>
          <CardTitle className="text-lg font-semibold text-primary mb-1">
            {plan.price}
          </CardTitle>
          <CardTitle className="text-sm text-muted-foreground font-normal">
            {plan.period}
          </CardTitle>
        </CardHeader>

        {/* Description */}
        <p className="text-sm text-muted-foreground mb-4">{plan.description}</p>

        {/* Slots highlight */}
        <div className="mb-4 px-4 py-3 bg-secondary/50 rounded-lg border border-border/50">
          <p className="text-sm font-semibold text-primary">{plan.slotsText}</p>
        </div>

        {/* Features */}
        <CardContent className="px-0 space-y-3 mb-6 text-sm text-muted-foreground">
          {plan.features.map((feature, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <Check className="w-3 h-3 text-primary mt-0.5 shrink-0" />
              <span>{feature}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  );
}
