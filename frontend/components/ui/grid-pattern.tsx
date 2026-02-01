"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const gridPatternVariants = cva(
  "absolute inset-0 pointer-events-none bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)]",
  {
    variants: {
      size: {
        default: "bg-[size:4rem_4rem]",
        sm: "bg-[size:2rem_2rem]",
        lg: "bg-[size:6rem_6rem]",
      },
      mask: {
        none: "",
        radial:
          "[mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_70%,transparent_100%)]",
        fade: "[mask-image:linear-gradient(to_bottom,transparent_0px,transparent_64px,black_200px,black_80%,transparent_100%)]",
      },
      position: {
        absolute: "absolute",
        fixed: "fixed",
      },
    },
    defaultVariants: {
      size: "default",
      mask: "radial",
      position: "absolute",
    },
  },
);

interface GridPatternProps
  extends
    React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof gridPatternVariants> {
  offsetX?: number;
  offsetY?: number;
}

export function GridPattern({
  className,
  size,
  mask,
  position,
  offsetX = 0,
  offsetY = 0,
  style,
  ...props
}: GridPatternProps) {
  return (
    <div
      className={cn(gridPatternVariants({ size, mask, position, className }))}
      style={{
        backgroundPosition: `${offsetX}px ${offsetY}px`,
        ...style,
      }}
      {...props}
    />
  );
}

export { gridPatternVariants };
