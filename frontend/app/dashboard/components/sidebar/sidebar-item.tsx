import { LinkButton } from "@/components/ui/link-button";
import { cn } from "@/lib/utils";
import { ArrowUpRight, LucideIcon } from "lucide-react";
import { ComponentProps } from "react";

interface SidebarItemProps extends ComponentProps<typeof LinkButton> {
  icon?: LucideIcon | React.ElementType;
  iconClassName?: string;
  startSlot?: React.ReactNode;
  active?: boolean;
}

export function SidebarItem({
  icon: Icon,
  iconClassName,
  startSlot,
  active = false,
  children,
  className,
  ...props
}: SidebarItemProps) {
  const opensNewTab = props.target === "_blank";

  return (
    <LinkButton
      variant="ghost"
      aria-current={active ? "page" : undefined}
      className={cn(
        "w-full justify-start gap-3 group relative overflow-hidden hover:bg-sidebar-accent hover:text-primary",
        "min-w-0 shrink-0",
        active && "bg-primary/10 text-primary hover:bg-primary/10",
        className,
      )}
      {...props}
    >
      {Icon && (
        <span className="flex w-8 shrink-0 justify-center">
          <Icon className={cn("size-5", iconClassName)} />
        </span>
      )}
      {startSlot && <>{startSlot}</>}
      <span className="truncate flex-1 text-left">{children}</span>
      {opensNewTab && (
        <>
          <ArrowUpRight
            aria-hidden
            className="size-3.5 shrink-0 text-muted-foreground transition-colors group-hover:text-primary"
          />
          <span className="sr-only">(새 탭에서 열림)</span>
        </>
      )}
    </LinkButton>
  );
}
