"use client";

import { RefObject, Suspense, useEffect, useRef } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { AvatarImage, AvatarFallback, Avatar } from "@/components/ui/avatar";
import { discordQueries } from "@/queries/discord";
import { useQuery } from "@tanstack/react-query";
import { SidebarItem } from "./sidebar-item";
import { SidebarItemSkeleton } from "./sidebar-item-skeleton";
import routeMap from "@/constants/route-map";
import { getDiscordIconUrl } from "@/lib/urls";
import { cn } from "@/lib/utils";
import { Loader2, RefreshCcw } from "lucide-react";

export default function Servers() {
  const listRef = useRef<HTMLDivElement>(null);

  return (
    <div className="flex-1 flex flex-col min-h-0 py-4 overflow-hidden">
      <div className="px-6 pb-2">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          내 서버
        </p>
      </div>

      <div
        ref={listRef}
        className="flex-1 overflow-y-auto space-y-1 px-3 flex flex-col"
      >
        <Suspense fallback={<ServerListSkeleton />}>
          <ServerList listRef={listRef} />
        </Suspense>
      </div>
    </div>
  );
}

function ServerList({
  listRef,
}: {
  listRef: RefObject<HTMLDivElement | null>;
}) {
  const { data, isLoading, isError, refetch, isFetching } = useQuery(
    discordQueries.guilds(),
  );
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const activeServerId =
    pathname === routeMap.DASHBOARD.SERVER_PATH ? searchParams.get("id") : null;

  useEffect(() => {
    const list = listRef.current;
    const item = list?.querySelector<HTMLElement>('[aria-current="page"]');
    if (!list || !item) return;

    const top = item.offsetTop - list.offsetTop;
    const bottom = top + item.offsetHeight;
    if (top < list.scrollTop) {
      list.scrollTop = top;
    } else if (bottom > list.scrollTop + list.clientHeight) {
      list.scrollTop = bottom - list.clientHeight;
    }
  }, [activeServerId, data, listRef]);

  if (isLoading) return <ServerListSkeleton />;

  if (isError) {
    return (
      <div className="px-3 py-2 text-xs text-muted-foreground">
        <p>서버 목록을 불러오지 못했습니다.</p>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={isFetching}
          className="mt-2 inline-flex items-center gap-1.5 font-medium text-primary hover:text-primary/80 disabled:opacity-50"
        >
          {isFetching ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RefreshCcw className="h-3.5 w-3.5" />
          )}
          다시 불러오기
        </button>
      </div>
    );
  }

  return data?.map((server) => {
    const active = server.id === activeServerId;

    return (
      <SidebarItem
        href={routeMap.DASHBOARD.SERVER(server.id)}
        key={server.id}
        active={active}
        startSlot={
          <Avatar
            className={cn(
              "w-8 h-8 border-2 border-border",
              active && "border-primary",
            )}
          >
            <AvatarImage
              src={getDiscordIconUrl(server.id, server.icon)}
              alt={server.name}
            />
            <AvatarFallback className="text-primary text-xs">
              {server.name.slice(0, 2)}
            </AvatarFallback>
          </Avatar>
        }
      >
        {server.name}
      </SidebarItem>
    );
  });
}

function ServerListSkeleton() {
  return Array.from({ length: 5 }).map((_, index) => (
    <SidebarItemSkeleton key={index} />
  ));
}
