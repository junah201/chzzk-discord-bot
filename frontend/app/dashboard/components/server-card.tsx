import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/link-button";
import routeMap from "@/constants/route-map";
import { Guild } from "@/types/api";
import { Users } from "lucide-react";

interface ServerCardProps {
  server: Guild;
}

export function ServerCard({ server }: ServerCardProps) {
  const iconUrl = server.icon
    ? `https://cdn.discordapp.com/icons/${server.id}/${server.icon}.webp?size=64`
    : undefined;

  return (
    <Card className="bg-card border-border transition-all duration-300 group hover:border-primary/50 h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-4">
          <Avatar className="w-16 h-16 border-2 border-border transition-colors">
            <AvatarImage src={iconUrl} alt={server.name} />
            <AvatarFallback className="bg-primary/20 text-primary text-lg font-semibold">
              {server.name.slice(0, 2)}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <CardTitle className="text-xl truncate group-hover:text-primary transition-colors">
              {server.name}
            </CardTitle>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Users className="w-4 h-4" />
            <span>
              {(server.approximate_member_count ?? 0).toLocaleString()} 멤버
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-auto">
        <LinkButton
          href={routeMap.DASHBOARD.SERVER(server.id)}
          variant="outline"
          className="w-full"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          관리하기
        </LinkButton>
      </CardContent>
    </Card>
  );
}
