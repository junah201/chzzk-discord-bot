import { LinkButton } from "@/components/ui/link-button";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { ComponentProps } from "react";

interface SidebarItemProps extends ComponentProps<typeof LinkButton> {
  icon?: LucideIcon | React.ElementType;
  startSlot?: React.ReactNode;
}

export function SidebarItem({
  icon: Icon,
  startSlot,
  children,
  className,
  ...props
}: SidebarItemProps) {
  return (
    <LinkButton
      variant="ghost"
      className={cn(
        "w-full justify-start gap-3 group relative overflow-hidden hover:bg-sidebar-accent hover:text-primary",
        "min-w-0 shrink-0",
        className,
      )}
      {...props}
    >
      {Icon && <Icon className="w-5 h-5 shrink-0" />}
      {startSlot && <>{startSlot}</>}
      <span className="truncate flex-1 text-left">{children}</span>
    </LinkButton>
  );
}
