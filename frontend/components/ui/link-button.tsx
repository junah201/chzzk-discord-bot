import { HTMLMotionProps } from "motion/react";
import { buttonVariants, ButtonInnerContent } from "./button";
import { VariantProps } from "class-variance-authority";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import Link from "next/link";

export interface LinkButtonProps
  extends
    Omit<HTMLMotionProps<"a">, "size" | "children">,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
  href: string;
  external?: boolean;
}

const isExternalUrl = (url: string) => {
  return (
    url.startsWith("http://") ||
    url.startsWith("https://") ||
    url.startsWith("mailto:") ||
    url.startsWith("//")
  );
};

const LinkButton = ({
  href,
  variant,
  size,
  effect,
  className,
  children,
  external,
  ...props
}: LinkButtonProps) => {
  const isExternal = external || isExternalUrl(href);

  const commonProps = {
    className: cn(buttonVariants({ variant, size, effect, className })),
    whileHover: { scale: 1.05 },
    whileTap: { scale: 0.95 },
    children: (
      <ButtonInnerContent effect={effect}>{children}</ButtonInnerContent>
    ),
    ...props,
  };

  if (isExternal) {
    return (
      <motion.a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...commonProps}
      />
    );
  }

  return (
    <Link href={href} legacyBehavior passHref>
      <motion.a {...commonProps} />
    </Link>
  );
};

LinkButton.displayName = "LinkButton";

export { LinkButton };
