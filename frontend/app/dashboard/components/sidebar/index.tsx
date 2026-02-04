import { Logo } from "@/components/ui/logo";
import { Separator } from "@/components/ui/separator";

import Profile from "./profile";
import Servers from "./servers";
import SidebarUtilities from "./sidebar-utilities";
import SidebarNavigation from "./sidebar-navigation";

export function DashboardSidebar() {
  return (
    <div className="flex flex-col h-full bg-sidebar border-r border-sidebar-border">
      <div className="p-6 ">
        <Logo size="md" />
      </div>
      <Separator />
      <SidebarNavigation />
      <Separator />
      <Servers />
      <Separator />
      <SidebarUtilities />
      <Separator />
      <div className="p-3">
        <Profile />
      </div>
    </div>
  );
}
