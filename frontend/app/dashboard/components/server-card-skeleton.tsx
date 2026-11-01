import { Skeleton } from "@/components/ui/skeleton";

export function ServerCardSkeleton() {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-border bg-card p-4">
      <Skeleton className="size-12 shrink-0 rounded-full" />
      <div className="flex min-w-0 flex-1 flex-col gap-2">
        <Skeleton className="h-5 w-2/3 max-w-48" />
        <Skeleton className="h-4 w-40" />
      </div>
    </div>
  );
}
