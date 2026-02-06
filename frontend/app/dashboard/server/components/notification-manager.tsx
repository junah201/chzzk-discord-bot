"use client";

import { fromNow, formatDate } from "@/lib/date";
import { useQuery } from "@tanstack/react-query";
import { motion } from "motion/react";

import { notificationQueries } from "@/queries/notifications";
import { Notification } from "@/types/api";
import { Button } from "@/components/ui/button";
import {
  PolicyTable,
  PolicyThead,
  PolicyTh,
  PolicyTr,
  PolicyTd,
} from "@/components/policy";
import {
  getChzzkChannelImageUrl,
  getChzzkChannelUrl,
  getDiscordChannelUrl,
} from "@/lib/urls";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { useNotificationActions } from "@/hooks/use-notifications";
import DeleteNotificationDialog from "./delete-notification-dialog";
import EditNotificationDialog from "./edit-notification-dialog";
import { ExternalLink, Loader2, Send } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

interface NotificationManagerProps {
  serverId: string;
}

export default function NotificationManager({
  serverId,
}: NotificationManagerProps) {
  const { data, isLoading } = useQuery(
    notificationQueries.listByGuildId(serverId),
  );

  const notifications = Array.isArray(data) ? data : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25, duration: 0.4 }}
      className="space-y-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">알림 목록</h2>
          <p className="text-sm text-muted-foreground mt-1">
            등록된 치지직 알림 채널들을 관리하고 테스트할 수 있습니다.
          </p>
        </div>
      </div>

      <div className="">
        {isLoading ? (
          <NotificationTableLoading />
        ) : notifications.length === 0 ? (
          <NotificationTableEmpty />
        ) : (
          <NotificationTable notifications={notifications} />
        )}
      </div>
    </motion.div>
  );
}

function NotificationTableLoading() {
  return (
    <div className="flex flex-col items-center justify-center py-20 bg-card/50 rounded-md border border-border overflow-hidden">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-3" />
      <p className="text-sm text-muted-foreground animate-pulse">
        알림 목록을 불러오는 중...
      </p>
    </div>
  );
}

function NotificationTableEmpty() {
  return (
    <div className="flex flex-col items-center justify-center py-16 bg-card/50 rounded-md border border-border overflow-hidden">
      <p className="text-sm text-muted-foreground font-medium">
        설정된 알림이 없습니다.
      </p>
      <p className="text-xs text-muted-foreground/60 mt-1">
        새로운 치지직 채널을 등록하여 알림을 받아보세요.
      </p>
    </div>
  );
}

function NotificationTable({
  notifications,
}: {
  notifications: Notification[];
}) {
  return (
    <PolicyTable className="min-w-full text-left">
      <PolicyThead className="bg-muted/50 border-b border-border">
        <PolicyTh className="w-48 pl-6">치지직 채널</PolicyTh>
        <PolicyTh className="min-w-50">디스코드 채널</PolicyTh>
        <PolicyTh className="min-w-50">최근 알림</PolicyTh>
        <PolicyTh className="w-40">테스트 알림</PolicyTh>
        <PolicyTh className="w-40">수정</PolicyTh>
        <PolicyTh className="w-40">삭제</PolicyTh>
      </PolicyThead>

      <tbody className="divide-y divide-border bg-background">
        {notifications.map((n) => (
          <NotificationRow key={`${n.PK}-${n.SK}`} notification={n} />
        ))}
      </tbody>
    </PolicyTable>
  );
}

function NotificationRow({ notification: n }: { notification: Notification }) {
  const { test } = useNotificationActions(n.guild_id);
  const chzzkId = n.chzzk_id || n.PK.split("#")[1] || "unknown";

  return (
    <PolicyTr className="group hover:bg-muted/40 transition-colors">
      <PolicyTd className="pl-6 py-4 flex items-center gap-2">
        <Avatar className="w-10 h-10 border border-border transition-colors">
          <AvatarImage
            src={getChzzkChannelImageUrl(n.chzzk_image_url)}
            alt={n.chzzk_name || chzzkId}
          />
          <AvatarFallback className="bg-primary/20 text-primary text-lg font-semibold">
            {(n.chzzk_name || chzzkId).slice(0, 2)}
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
          <a
            href={getChzzkChannelUrl(chzzkId)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 font-medium text-foreground hover:text-primary transition-colors w-fit"
          >
            {n.chzzk_name || "치지직 채널"}
            <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
          </a>
          <span className="text-xs text-muted-foreground font-mono mt-0.5">
            {chzzkId}
          </span>
        </div>
      </PolicyTd>

      <PolicyTd>
        <a
          href={getDiscordChannelUrl(n.guild_id, n.channel_id)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-500 text-sm font-medium hover:bg-indigo-500/20 transition-colors"
        >
          <span className="text-xs">#</span>
          {n.channel_name || "채널 이동"}
        </a>
      </PolicyTd>

      <PolicyTd>
        {n.last_noti_at ? (
          <div className="flex items-center gap-1.5">
            <Tooltip delayDuration={200}>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-1.5 text-sm text-foreground/90 hover:text-primary cursor-help transition-colors">
                  <span className="font-medium">{fromNow(n.last_noti_at)}</span>
                </div>
              </TooltipTrigger>
              <TooltipContent className="text-xs bg-foreground text-background">
                {formatDate(n.last_noti_at, "YYYY년 MM월 DD일 HH:mm:ss")}
              </TooltipContent>
            </Tooltip>

            <div
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-sm font-medium transition-colors cursor-default",
                n.last_noti_status === "SUCCESS"
                  ? "bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20"
                  : "bg-rose-500/10 text-rose-600 hover:bg-rose-500/20",
              )}
            >
              {n.last_noti_status === "SUCCESS" ? (
                <>전송 성공</>
              ) : (
                <>전송 실패</>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-muted-foreground/50 py-1">
            <span className="text-sm">이력 없음</span>
          </div>
        )}
      </PolicyTd>

      <PolicyTd>
        <Button
          size="sm"
          variant="secondary"
          onClick={() =>
            test.mutate({
              guild_id: n.guild_id,
              channel_id: n.channel_id,
              chzzk_id: chzzkId,
            })
          }
        >
          <Send className="h-4 w-4" />
          테스트 알림 보내기
        </Button>
      </PolicyTd>

      <PolicyTd>
        <EditNotificationDialog notification={n} />
      </PolicyTd>

      <PolicyTd>
        <DeleteNotificationDialog notification={n} />
      </PolicyTd>
    </PolicyTr>
  );
}
