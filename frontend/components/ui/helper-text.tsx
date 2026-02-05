import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const helperTextVariants = cva("text-xs font-medium text-destructive", {
  variants: {
    variant: {
      default: "text-inherit",
      destructive: "text-destructive",
    },
    defaultVariants: {
      variant: "default",
    },
  },
});

export interface HelperTextProps
  extends
    React.HTMLAttributes<HTMLParagraphElement>,
    VariantProps<typeof helperTextVariants> {}

const HelperText = React.forwardRef<HTMLParagraphElement, HelperTextProps>(
  ({ className, variant, children, ...props }, ref) => (
    <p
      className={cn(helperTextVariants({ variant, className }))}
      ref={ref}
      {...props}
    >
      {children}
    </p>
  ),
);
HelperText.displayName = "HelperText";

export { HelperText, helperTextVariants as HelperTextVariants };
