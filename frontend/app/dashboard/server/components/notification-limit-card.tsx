"use client";

import { motion } from "motion/react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Bell } from "lucide-react";
import Link from "next/link";
import routeMap from "@/constants/route-map";

interface NotificationLimitCardProps {
  currentCount: number;
  maxLimit: number;
}

export default function NotificationLimitCard({
  currentCount,
  maxLimit,
}: NotificationLimitCardProps) {
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

          <Progress value={percentage} className="h-2" />

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2 border-t border-border/60">
            <p className="text-sm text-muted-foreground">
              더 많은 알림이 필요하신가요?{" "}
              <Link
                href={routeMap.REDIRECTS.SUPPORT_SERVER}
                target="_blank"
                className="text-primary underline"
              >
                서포트 서버
              </Link>
              에 방문하여 문의해주세요.
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
