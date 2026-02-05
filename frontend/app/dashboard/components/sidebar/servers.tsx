import { AvatarImage, AvatarFallback, Avatar } from "@/components/ui/avatar";
import { discordQueries } from "@/queries/discord";
import { useQuery } from "@tanstack/react-query";
import { SidebarItem } from "./sidebar-item";
import { SidebarItemSkeleton } from "./sidebar-item-skeleton";
import routeMap from "@/constants/route-map";

export default function Servers() {
  const { data, isLoading } = useQuery(discordQueries.guilds());

  return (
    <div className="flex-1 flex flex-col min-h-0 py-4 overflow-hidden">
      <div className="px-6 pb-2">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          내 서버
        </p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1 px-3 flex flex-col">
        {data?.map((server) => (
          <SidebarItem
            href={routeMap.DASHBOARD.SERVER(server.id)}
            key={server.id}
            startSlot={
              <Avatar className="w-8 h-8 border-2 border-border">
                <AvatarImage
                  src={`https://cdn.discordapp.com/icons/${server.id}/${server.icon}.webp?size=64`}
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
        ))}
        {isLoading &&
          Array.from({ length: 5 }).map((_, index) => (
            <SidebarItemSkeleton key={index} />
          ))}
      </div>
    </div>
  );
}
