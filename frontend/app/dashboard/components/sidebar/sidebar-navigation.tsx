import routeMap from "@/constants/route-map";
import { LayoutGrid } from "lucide-react";
import { SidebarItem } from "./sidebar-item";

export default function SidebarNavigation() {
  return (
    <div className="px-3 py-4">
      <SidebarItem icon={LayoutGrid} href={routeMap.DASHBOARD.HOME}>
        서버 목록
      </SidebarItem>
    </div>
  );
}
