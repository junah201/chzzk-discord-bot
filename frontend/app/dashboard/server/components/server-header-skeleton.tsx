import { Skeleton } from "@/components/ui/skeleton";
import routeMap from "@/constants/route-map";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ServerHeaderSkeleton() {
  return (
    <div className="border-b border-border bg-background/95 backdrop-blur-lg">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Link
          href={routeMap.DASHBOARD.HOME}
          className="flex items-center gap-2 px-2.5 py-2.5 text-base rounded-lg hover:bg-muted"
        >
          <ArrowLeft className="w-4 h-4" />
          서버 목록으로 돌아가기
        </Link>

        <div className="flex items-center gap-4 mt-2">
          <Skeleton className="w-20 h-20 rounded-full border-2 border-muted" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-8 sm:h-10 w-48 sm:w-64" />
            <Skeleton className="h-4 w-40" />
          </div>
        </div>
      </div>
    </div>
  );
}
