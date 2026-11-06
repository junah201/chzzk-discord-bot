"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

const COPIED_MESSAGE = "클립보드에 복사했습니다";

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
  const [announcement, setAnnouncement] = useState("");
  const resetTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const announceTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(
    () => () => {
      clearTimeout(resetTimer.current);
      clearTimeout(announceTimer.current);
    },
    [],
  );

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      clearTimeout(resetTimer.current);
      clearTimeout(announceTimer.current);
      setCopied(true);
      // 같은 문구가 그대로 남아 있으면 스크린 리더가 다시 읽지 않으므로 비웠다가 채운다
      setAnnouncement("");
      announceTimer.current = setTimeout(
        () => setAnnouncement(COPIED_MESSAGE),
        100,
      );
      resetTimer.current = setTimeout(() => {
        setCopied(false);
        setAnnouncement("");
      }, 2000);
    } catch (error) {
      console.error(`${label} 실패:`, error);
    }
  };

  return (
    <>
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
      <span role="status" aria-live="polite" className="sr-only">
        {announcement}
      </span>
    </>
  );
}
