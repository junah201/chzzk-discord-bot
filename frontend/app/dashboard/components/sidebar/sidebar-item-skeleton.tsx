import { Skeleton } from "@/components/ui/skeleton";

export function SidebarItemSkeleton() {
  return (
    <div className="flex w-full items-center gap-3 px-6 py-2.5 overflow-hidden min-w-0">
      <Skeleton className="h-8 w-8 rounded-full shrink-0" />
      <Skeleton className="h-4 w-32 rounded-md" />
    </div>
  );
}
