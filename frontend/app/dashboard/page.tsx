"use client";

import { PolicyCallout } from "@/components/policy";
import routeMap from "@/constants/route-map";
import { discordQueries } from "@/queries/discord";
import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { ServerCard } from "./components/server-card";
import { ServerCardSkeleton } from "./components/server-card-skeleton";

export default function Dashboard() {
  const { data, isLoading } = useQuery(discordQueries.guilds());

  const servers = data || [];

  return (
    <div className="min-h-screen bg-background">
      <div className="relative z-10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold">내 서버</h2>
                <p className="text-sm text-muted-foreground mt-1">
                  관리 중인 디스코드 서버 목록
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {isLoading
                ? Array.from({ length: 12 }).map((_, index) => (
                    <div key={index}>
                      <ServerCardSkeleton />
                    </div>
                  ))
                : servers.map((server) => (
                    <motion.div
                      key={server.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ServerCard server={server} />
                    </motion.div>
                  ))}
            </div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              <PolicyCallout title="서버가 목록에 없나요?">
                관리자 권한을 가진 서버만 표시됩니다. 해당 서버에 관리자 권한이
                있는지 확인해주세요.
              </PolicyCallout>
              <PolicyCallout title="도움이 필요하신가요?">
                도움이 필요하신 경우,{" "}
                <a
                  href={routeMap.REDIRECTS.SUPPORT_SERVER}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary underline"
                >
                  서포트 서버
                </a>
                에 방문하여 문의해주세요.
              </PolicyCallout>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
