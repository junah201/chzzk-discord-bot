import Link from "next/link";
import { Bell, ChevronRight, Users } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import routeMap from "@/constants/route-map";
import { DEFAULT_SLOT_LIMIT } from "@/constants/slots";
import { getDiscordIconUrl } from "@/lib/urls";
import { Guild } from "@/types/api";

interface ServerCardProps {
  server: Guild;
}

/** 카드 전체가 서버 관리 페이지로 가는 링크 */
export function ServerCard({ server }: ServerCardProps) {
  return (
    <Link
      href={routeMap.DASHBOARD.SERVER(server.id)}
      className="group flex items-center gap-4 rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/50 focus-visible:border-primary focus-visible:outline-none"
    >
      <Avatar className="size-12 shrink-0 border border-border">
        <AvatarImage
          src={getDiscordIconUrl(server.id, server.icon)}
          alt={server.name}
        />
        <AvatarFallback className="bg-primary/20 font-semibold text-primary">
          {server.name.slice(0, 2)}
        </AvatarFallback>
      </Avatar>

      <div className="min-w-0 flex-1">
        <p className="truncate font-semibold transition-colors group-hover:text-primary">
          {server.name}
        </p>
        <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Users className="size-3.5" />
            멤버 {(server.approximate_member_count ?? 0).toLocaleString()}명
          </span>
          <span className="flex items-center gap-1">
            <Bell className="size-3.5" />
            알림 {server.current_count || 0}/
            {server.max_limit || DEFAULT_SLOT_LIMIT}개
          </span>
        </div>
      </div>

      <ChevronRight className="size-5 shrink-0 text-muted-foreground/50 transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
    </Link>
  );
}
