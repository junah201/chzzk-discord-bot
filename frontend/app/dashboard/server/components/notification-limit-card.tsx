"use client";

import { motion } from "motion/react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Bell } from "lucide-react";
import Link from "next/link";
import routeMap from "@/constants/route-map";
import { PolicyCallout } from "@/components/policy/policy-callout";

interface NotificationLimitCardProps {
  currentCount: number;
  maxLimit: number;
}

export default function NotificationLimitCard({
  currentCount,
  maxLimit,
}: NotificationLimitCardProps) {
  const isOverLimit = currentCount > maxLimit;
  const percentage = Math.min(100, (currentCount / maxLimit) * 100);

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
              <span className="font-semibold">알림 슬롯 현황</span>
            </div>
            <span className="text-sm font-bold">
              {currentCount} / {maxLimit}개 사용 중
            </span>
          </div>

          <Progress
            value={percentage}
            className={`h-2 ${isOverLimit ? "[&>div]:bg-destructive" : ""}`}
          />

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2 border-t border-border/60">
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
          </div>
        </CardContent>
      </Card>
      {isOverLimit && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <PolicyCallout
            variant="warning"
            title="알림 슬롯을 초과했습니다"
          >
            <ul className="mb-0 list-disc pl-5 text-sm">
              <li>
                등록된 알림이 슬롯 수({maxLimit}개)보다 많아서 알림을 추가하거나 수정할 수 없습니다.
              </li>
              <li>
                이미 등록된 알림도 모두 전송되지 않습니다.
              </li>
              <li>
                알림을 삭제하거나 슬롯을 늘린 뒤 다시 이용해 주세요.
              </li>
            </ul>
          </PolicyCallout>
        </motion.div>
      )}
    </motion.div>
  );
}
