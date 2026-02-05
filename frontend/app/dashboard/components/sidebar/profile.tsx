import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ChevronDown, User, Settings, LogOut } from "lucide-react";
import Link from "next/link";
import routeMap from "@/constants/route-map";

export default function Profile() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="w-full px-3 h-auto py-3 hover:bg-sidebar-accent group"
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <Avatar className="w-10 h-10 border-2 border-primary/30 group-hover:border-primary transition-colors">
              <AvatarFallback className="bg-primary/20 text-primary font-semibold">
                JH
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 text-left min-w-0">
              <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                junah201
              </p>
              <p className="text-xs text-muted-foreground truncate">관리자</p>
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
