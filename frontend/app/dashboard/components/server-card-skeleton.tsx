import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function ServerCardSkeleton() {
  return (
    <Card className="bg-card border-border h-full flex flex-col">
      <CardHeader className="w-full min-w-0">
        <div className="flex items-center gap-4 w-full min-w-0">
          <Skeleton className="w-16 h-16 rounded-full shrink-0" />

          <div className="flex-1 min-w-0">
            <Skeleton className="h-7 w-2/3 max-w-50" />
          </div>

          <div className="flex flex-col gap-2 items-end shrink-0">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
      </CardHeader>

      <CardContent className="mt-auto">
        <Skeleton className="h-10 w-full rounded-md" />
      </CardContent>
    </Card>
  );
}