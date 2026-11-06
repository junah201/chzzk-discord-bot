"use client";

import { useState, type ReactNode } from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

interface CopyButtonProps {
  value: string;
  label: string;
  children: ReactNode;
  className?: string;
  iconClassName?: string;
}

export default function CopyButton({
  value,
  label,
  children,
  className,
  iconClassName,
}: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error(`${label} 실패:`, error);
    }
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      title={label}
      aria-label={label}
      className={cn(
        "inline-flex items-center text-muted-foreground hover:text-foreground transition-colors cursor-pointer",
        className,
      )}
    >
      {children}
      {copied ? (
        <Check className={cn("text-green-500", iconClassName)} />
      ) : (
        <Copy className={iconClassName} />
      )}
    </button>
  );
}
