"use client";

import { useState } from "react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { routeMap } from "@/constants/route-map";
import { getDiscordIconUrl } from "@/lib/urls";
import { Guild } from "@/types/api";
import { ArrowLeft, Check, Copy } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";

interface ServerHeaderProps {
  server: Guild;
}

export default function ServerHeader({ server }: ServerHeaderProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyId = async () => {
    try {
      await navigator.clipboard.writeText(server.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("서버 ID 복사 실패:", error);
    }
  };

  return (
    <div className="border-b border-border bg-background/95 backdrop-blur-lg">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Link
            href={routeMap.DASHBOARD.HOME}
            className="flex items-center gap-2 px-2.5 py-2.5 text-base rounded-lg hover:bg-muted w-fit"
          >
            <ArrowLeft className="w-4 h-4" />
            서버 목록으로 돌아가기
          </Link>

          <div className="flex items-center gap-4 mt-2">
            <Avatar className="w-20 h-20 border-2 border-primary/30">
              <AvatarImage
                src={getDiscordIconUrl(server.id, server.icon)}
                alt={server.name}
              />
              <AvatarFallback className="bg-primary/20 text-primary text-2xl font-semibold">
                {server.name.slice(0, 2)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h1 className="text-3xl sm:text-4xl font-bold bg-linear-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
                {server.name}
              </h1>

              <div className="flex items-center gap-2 mt-1">
                <p className="hidden sm:inline text-sm text-muted-foreground">
                  치지직 방송 알림을 관리하세요
                </p>
                <span className="hidden sm:inline text-muted-foreground/40">
                  •
                </span>
                <button
                  onClick={handleCopyId}
                  className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground bg-muted/50 hover:bg-muted px-2 py-1 rounded-md transition-colors cursor-pointer"
                  title="클립보드에 서버 ID 복사"
                >
                  <span className="font-mono">ID: {server.id}</span>
                  {copied ? (
                    <Check className="w-3.5 h-3.5 text-green-500" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
