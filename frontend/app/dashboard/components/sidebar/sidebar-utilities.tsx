import routeMap from "@/constants/route-map";
import { FileText, MessageSquare } from "lucide-react";
import { SidebarItem } from "./sidebar-item";

export default function SidebarUtilities() {
  return (
    <div className="px-3 py-4 space-y-1">
      <SidebarItem
        icon={MessageSquare}
        href={routeMap.REDIRECTS.SUPPORT_SERVER}
        target="_blank"
      >
        서포트 서버
      </SidebarItem>
      <SidebarItem
        icon={FileText}
        href={routeMap.DOCS.HOME}
        target="_blank"
        rel="noopener noreferrer"
      >
        문서
      </SidebarItem>
    </div>
  );
}
