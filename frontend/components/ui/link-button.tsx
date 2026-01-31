import { HTMLMotionProps } from "motion/react";
import { buttonVariants, ButtonInnerContent } from "./button";
import { VariantProps } from "class-variance-authority";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

export interface LinkButtonProps
  extends
    Omit<HTMLMotionProps<"a">, "size" | "children">,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
  href: string;
}

const LinkButton = ({
  href,
  variant,
  size,
  effect,
  className,
  children,
  ...props
}: LinkButtonProps) => {
  return (
    <motion.a
      href={href}
      className={cn(buttonVariants({ variant, size, effect, className }))}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      {...props}
    >
      <ButtonInnerContent effect={effect}>{children}</ButtonInnerContent>
    </motion.a>
  );
};

LinkButton.displayName = "LinkButton";

export { LinkButton };
