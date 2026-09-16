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
              더 많은 알림이 필요하신가요?{" "}
              <Link
                href={routeMap.PRICING}
                target="_blank"
                className="text-primary underline"
              >
                요금제 페이지
              </Link>
              를 확인해보세요.
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
            title="허용된 알림 슬롯 개수를 초과했습니다"
          >
            <ul className="mb-0 list-disc pl-5 text-sm">
              <li>
                현재 서버에 등록된 알림 개수가 최대 허용 슬롯({maxLimit}
                개)을 초과하여 설정을 수정하거나 추가할 수 없습니다.
              </li>
              <li>
                기존 등록된 모든 알림은 비활성화되었으며, 알림이 정상적으로
                전송되지 않습니다.
              </li>
              <li>
                초과된 알림을 정리(삭제)하거나 슬롯을 확장한 후 다시 이용해
                주세요.
              </li>
            </ul>
          </PolicyCallout>
        </motion.div>
      )}
    </motion.div>
  );
}
