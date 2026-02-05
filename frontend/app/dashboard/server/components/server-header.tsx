"use client";

import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { routeMap } from "@/constants/route-map";
import { getDiscordIconUrl } from "@/lib/urls";
import { Guild } from "@/types/api";
import { ArrowLeft } from "lucide-react";
import { motion } from "motion/react";
import Link from "next/link";

interface ServerHeaderProps {
  server: Guild;
}

export default function ServerHeader({ server }: ServerHeaderProps) {
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
            className="flex items-center gap-2 px-2.5 py-2.5 text-base rounded-lg hover:bg-muted"
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
              <p className="text-sm text-muted-foreground mt-1">
                치지직 방송 알림을 관리하세요
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
