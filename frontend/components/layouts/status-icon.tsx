import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatusIconProps {
  icon: ReactNode;
  badge?: ReactNode;
  glowClassName?: string;
}

export function StatusIcon({
  icon,
  badge,
  glowClassName = "bg-primary/20",
}: StatusIconProps) {
  return (
    <>
      <div
        className={cn("absolute inset-0 blur-2xl rounded-full", glowClassName)}
      />
      <div className="relative bg-card border border-border rounded-3xl p-6 shadow-2xl">
        <div className="w-16 h-16 text-muted-foreground flex items-center justify-center [&>svg]:w-full [&>svg]:h-full">
          {icon}
        </div>

        {badge && (
          <div className="absolute -bottom-2 -right-2 bg-destructive text-destructive-foreground p-2 rounded-full border-4 border-background">
            <div className="w-6 h-6 flex items-center justify-center [&>svg]:w-full [&>svg]:h-full">
              {badge}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
