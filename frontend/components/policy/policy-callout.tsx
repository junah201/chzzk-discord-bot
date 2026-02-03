import { cn } from "@/lib/utils";
import { cva, VariantProps } from "class-variance-authority";
import { AlertCircle, AlertTriangle } from "lucide-react";

const policyCalloutVariants = cva("p-4 rounded-lg border my-4", {
  variants: {
    variant: {
      info: "bg-secondary/30 border-border/50",
      warning: "bg-amber-500/5 border-amber-500/20",
    },
  },
  defaultVariants: {
    variant: "info",
  },
});

const policyCalloutTitleVariants = cva("font-semibold mb-1", {
  variants: {
    variant: {
      info: "text-primary",
      warning: "text-amber-500",
    },
  },
  defaultVariants: {
    variant: "info",
  },
});

const iconVariants = cva("h-5 w-5 mt-0.5 shrink-0", {
  variants: {
    variant: {
      info: "text-primary",
      warning: "text-amber-500",
    },
  },
  defaultVariants: {
    variant: "info",
  },
});

const ICONS = {
  info: AlertCircle,
  warning: AlertTriangle,
} as const;

export interface PolicyCalloutProps
  extends
    React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof policyCalloutVariants> {
  title: string;
}

export function PolicyCallout({
  variant,
  title,
  children,
  className,
}: PolicyCalloutProps) {
  const Icon = ICONS[variant || "info"];

  return (
    <div className={cn(policyCalloutVariants({ variant }), className)}>
      <div className="flex items-start gap-3">
        <Icon className={cn(iconVariants({ variant }))} />
        <div className="text-sm">
          {title && (
            <p className={cn(policyCalloutTitleVariants({ variant }))}>
              {title}
            </p>
          )}
          <div className="text-foreground/90 leading-relaxed">{children}</div>
        </div>
      </div>
    </div>
  );
}
