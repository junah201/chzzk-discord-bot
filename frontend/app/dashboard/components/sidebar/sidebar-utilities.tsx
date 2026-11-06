import routeMap from "@/constants/route-map";
import { SiDiscord } from "@icons-pack/react-simple-icons";
import { BookOpen } from "lucide-react";
import { SidebarItem } from "./sidebar-item";

export default function SidebarUtilities() {
  return (
    <div className="px-3 py-4 space-y-1">
      <SidebarItem
        icon={SiDiscord}
        iconClassName="size-4.5"
        href={routeMap.REDIRECTS.SUPPORT_SERVER}
        target="_blank"
        rel="noopener noreferrer"
      >
        서포트 서버
      </SidebarItem>
      <SidebarItem
        icon={BookOpen}
        href={routeMap.DOCS.HOME}
        target="_blank"
        rel="noopener noreferrer"
      >
        문서
      </SidebarItem>
    </div>
  );
}
