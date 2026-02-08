import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ChevronDown, User, Settings, LogOut } from "lucide-react";
import Link from "next/link";
import routeMap from "@/constants/route-map";
import { useQuery } from "@tanstack/react-query";
import { discordQueries } from "@/queries/discord";
import { Skeleton } from "@/components/ui/skeleton";
import { getDiscordUserAvatarUrl } from "@/lib/urls";

export default function Profile() {
  const { data, isLoading } = useQuery(discordQueries.me());

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="w-full px-3 h-auto py-3 hover:bg-sidebar-accent group"
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {isLoading ? (
              <Skeleton className="h-10 w-10 rounded-full" />
            ) : (
              <Avatar className="w-10 h-10 border-2 border-primary/30 group-hover:border-primary transition-colors">
                <AvatarImage
                  src={getDiscordUserAvatarUrl(data?.id, data?.avatar)}
                  alt={data?.username}
                />
                <AvatarFallback className="bg-primary/20 text-primary font-semibold">
                  {data?.username.slice(0, 2)}
                </AvatarFallback>
              </Avatar>
            )}
            <div className="flex-1 text-left min-w-0">
              {isLoading ? (
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-12" />
                </div>
              ) : (
                <>
                  <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                    {data?.username}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    관리자
                  </p>
                </>
              )}
            </div>
          </div>
          <ChevronDown className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="center"
        alignOffset={-8}
        side="top"
        sideOffset={8}
        className="w-56 bg-popover border-border"
      >
        <DropdownMenuLabel className="text-xs text-muted-foreground">
          내 계정
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="gap-2 cursor-pointer hover:bg-primary/10 hover:text-primary">
          <User className="w-4 h-4" />
          <span>내 정보</span>
        </DropdownMenuItem>
        <DropdownMenuItem className="gap-2 cursor-pointer hover:bg-primary/10 hover:text-primary">
          <Settings className="w-4 h-4" />
          <span>설정</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="gap-2 cursor-pointer hover:bg-destructive/10 text-destructive hover:text-destructive"
          asChild
        >
          <Link href={routeMap.AUTH.LOGOUT}>
            <LogOut className="w-4 h-4" />
            <span>로그아웃</span>
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
