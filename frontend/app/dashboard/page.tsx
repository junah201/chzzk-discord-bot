"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Info, Search } from "lucide-react";
import routeMap from "@/constants/route-map";
import { discordQueries } from "@/queries/discord";
import { ServerCard } from "./components/server-card";
import { ServerCardSkeleton } from "./components/server-card-skeleton";

// 서버가 이 개수 이상일 때만 검색창을 보여줌
const SEARCH_THRESHOLD = 8;

export default function Dashboard() {
  const { data: servers = [], isLoading } = useQuery(discordQueries.guilds());
  const [keyword, setKeyword] = useState("");

  const showSearch = servers.length >= SEARCH_THRESHOLD;
  const normalized = keyword.trim().toLowerCase();
  const filtered = normalized
    ? servers.filter((server) =>
        server.name.toLowerCase().includes(normalized),
      )
    : servers;

  return (
    <div className="min-h-screen bg-background">
      <div className="relative z-10">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="text-2xl font-bold">내 서버</h2>
                <p className="mt-1 flex items-start gap-1.5 text-sm text-muted-foreground break-keep">
                  <Info className="mt-0.5 size-3.5 shrink-0" />
                  {/* 검색창이 옆에 있는 넓은 화면에서만 두 줄로 나누고, 그 밖에는 한 문단으로 이어짐 */}
                  <span>
                    <span className={showSearch ? "md:block" : undefined}>
                      관리자 권한이 있는 디스코드 서버만 보입니다.
                    </span>{" "}
                    <span className={showSearch ? "md:block" : undefined}>
                      궁금한 점은{" "}
                      <Link
                        href={routeMap.REDIRECTS.SUPPORT_SERVER}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary underline underline-offset-2"
                      >
                        서포트 서버
                      </Link>
                      에 문의해 주세요.
                    </span>
                  </span>
                </p>
              </div>

              {showSearch && (
                <label className="relative block w-full md:w-72">
                  <span className="sr-only">서버 검색</span>
                  <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="search"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    placeholder="서버 이름으로 검색"
                    className="h-10 w-full rounded-lg border border-border bg-card pr-3 pl-9 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-primary/60"
                  />
                </label>
              )}
            </div>

            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 2xl:grid-cols-3">
              {isLoading
                ? Array.from({ length: 12 }).map((_, index) => (
                    <ServerCardSkeleton key={index} />
                  ))
                : filtered.map((server) => (
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

            {!isLoading && normalized && filtered.length === 0 && (
              <p className="py-12 text-center text-sm text-muted-foreground">
                ‘{keyword.trim()}’(이)가 들어간 서버가 없습니다.
              </p>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
