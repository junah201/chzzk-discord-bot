"use client";

import { use, useId } from "react";
import { motion } from "motion/react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Bell, RefreshCw } from "lucide-react";
import Link from "next/link";
import routeMap from "@/constants/route-map";
import { PolicyCallout } from "@/components/policy/policy-callout";
import { useSyncSlots } from "@/hooks/use-sync-slots";
import MutationAlert from "./mutation-alert";
import { ServerContext } from "../server-context";

interface NotificationLimitCardProps {
  slots?: { currentCount: number; maxLimit: number };
}

export default function NotificationLimitCard({
  slots,
}: NotificationLimitCardProps) {
  const titleId = useId();
  const { serverId } = use(ServerContext);
  const syncSlots = useSyncSlots(serverId);
  const syncSuccessMessage =
    syncSlots.data &&
    (syncSlots.data.current_count === syncSlots.data.previous_count
      ? "슬롯 개수가 이미 실제 알림 수와 같습니다."
      : `사용 중인 슬롯을 ${syncSlots.data.previous_count}개에서 ${syncSlots.data.current_count}개로 갱신했습니다.`);
  const isOverLimit = slots ? slots.currentCount > slots.maxLimit : false;
  const percentage = slots
    ? Math.min(100, (slots.currentCount / slots.maxLimit) * 100)
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05, duration: 0.4 }}
    >
      <Card className="bg-card border-border shadow-sm">
        <CardContent className="px-6 flex flex-col gap-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              <span id={titleId} className="font-semibold">
                알림 슬롯 현황
              </span>
            </div>
            {slots ? (
              <span className="text-sm font-bold">
                {slots.currentCount} / {slots.maxLimit}개 사용 중
              </span>
            ) : (
              <Skeleton className="h-5 w-24" />
            )}
          </div>

          {slots ? (
            <Progress
              value={percentage}
              aria-labelledby={titleId}
              getValueLabel={() =>
                `${slots.maxLimit}개 중 ${slots.currentCount}개 사용 중`
              }
              className={`h-2 ${isOverLimit ? "[&>div]:bg-destructive" : ""}`}
            />
          ) : (
            <Skeleton className="h-2 w-full rounded-full" />
          )}

          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-1 lg:gap-3 pt-2 border-t border-border/60">
            <p className="text-sm text-muted-foreground">
              알림이 더 필요하다면{" "}
              <Link
                href={routeMap.PRICING}
                target="_blank"
                className="text-primary underline"
              >
                요금제
              </Link>
              를 확인해 보세요.
            </p>
            <p className="text-sm text-muted-foreground">
              슬롯 개수가 실제 알림 수와 다르면{" "}
              <button
                type="button"
                onClick={() => syncSlots.mutate()}
                disabled={syncSlots.isPending}
                className="cursor-pointer whitespace-nowrap text-primary underline disabled:cursor-not-allowed disabled:opacity-50"
              >
                <RefreshCw
                  className={`inline-block mr-1 size-3.5 align-[-0.125em] ${syncSlots.isPending ? "animate-spin" : ""}`}
                />
                강제 새로고침
              </button>
              을 눌러 주세요.
            </p>
          </div>
          <MutationAlert
            error={syncSlots.error}
            isSuccess={syncSlots.isSuccess}
            errorTitle="슬롯 개수를 새로고침하지 못했습니다"
            successMessage={syncSuccessMessage}
            onClose={syncSlots.reset}
            className="-mt-2"
          />
        </CardContent>
      </Card>
      {isOverLimit && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <PolicyCallout variant="warning" title="알림 슬롯을 초과했습니다">
            <ul className="mb-0 list-disc pl-5 text-sm">
              <li>
                등록된 알림이 슬롯 수({slots?.maxLimit}개)보다 많아서 알림을
                추가하거나 수정할 수 없습니다.
              </li>
              <li>이미 등록된 알림도 모두 전송되지 않습니다.</li>
              <li>알림을 삭제하거나 슬롯을 늘린 뒤 다시 이용해 주세요.</li>
            </ul>
          </PolicyCallout>
        </motion.div>
      )}
    </motion.div>
  );
}
