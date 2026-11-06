"use client";

import { CSSProperties, useState } from "react";
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
import { DISCORD_COLORS } from "@/lib/discord";
import { useNotificationActions } from "@/hooks/use-notifications";
import DeleteNotificationDialog from "./delete-notification-dialog";
import EditNotificationDialog from "./edit-notification-dialog";
import { ExternalLink, Loader2, Send } from "lucide-react";
import CopyButton from "@/components/copy-button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { getErrorMessage } from "@/lib/api-error";
import { Feedback, getNotificationLabel } from "./mutation-alert";
import TestGuideCallout from "./test-guide-callout";

interface NotificationManagerProps {
  serverId: string;
  isSubscription?: boolean;
}

export default function NotificationManager({
  serverId,
  isSubscription = false,
}: NotificationManagerProps) {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    ...notificationQueries.listByGuildId(serverId),
    meta: { inlineError: true },
  });
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [feedbackKey, setFeedbackKey] = useState(0);

  const handleFeedback = (next: Feedback) => {
    setFeedback(next);
    setFeedbackKey((key) => key + 1);
  };

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
            등록한 알림을 수정하거나 테스트 알림을 보낼 수 있습니다.
          </p>
        </div>
      </div>

      {feedback && (
        <Alert
          key={feedbackKey}
          variant={feedback.variant}
          onClose={() => setFeedback(null)}
        >
          <AlertTitle>{feedback.title}</AlertTitle>
          {feedback.description && (
            <AlertDescription className="whitespace-pre-line">
              {feedback.description}
            </AlertDescription>
          )}
        </Alert>
      )}
      {feedback?.showTestGuide && <TestGuideCallout />}

      <div className="">
        {isLoading ? (
          <NotificationTableLoading />
        ) : isError ? (
          <Alert variant="destructive">
            <AlertTitle>알림 목록을 불러오지 못했습니다</AlertTitle>
            <AlertDescription>
              <p>{getErrorMessage(error)}</p>
              <Button
                size="sm"
                variant="outline"
                className="mt-3"
                disabled={isFetching}
                onClick={() => refetch()}
              >
                {isFetching && <Loader2 className="h-4 w-4 animate-spin" />}
                다시 시도
              </Button>
            </AlertDescription>
          </Alert>
        ) : notifications.length === 0 ? (
          <NotificationTableEmpty />
        ) : (
          <NotificationTable
            notifications={notifications}
            isSubscription={isSubscription}
            onFeedback={handleFeedback}
          />
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
        아직 등록한 알림이 없습니다.
      </p>
      <p className="text-xs text-muted-foreground/60 mt-1">
        위의 알림 추가에서 치지직 채널을 등록해 보세요.
      </p>
    </div>
  );
}

function NotificationTable({
  notifications,
  isSubscription,
  onFeedback,
}: {
  notifications: Notification[];
  isSubscription?: boolean;
  onFeedback: (feedback: Feedback) => void;
}) {
  return (
    <PolicyTable className="min-w-full text-left">
      <PolicyThead className="bg-muted/50 border-b border-border">
        <PolicyTh className="whitespace-nowrap pl-6">치지직 채널</PolicyTh>
        <PolicyTh className="whitespace-nowrap">디스코드 채널</PolicyTh>
        <PolicyTh className="whitespace-nowrap">최근 알림</PolicyTh>
        <PolicyTh className="w-40">테스트 알림</PolicyTh>
        <PolicyTh className="w-40">수정</PolicyTh>
        <PolicyTh className="w-40">삭제</PolicyTh>
      </PolicyThead>

      <tbody className="divide-y divide-border bg-background">
        {notifications.map((n) => (
          <NotificationRow
            key={`${n.chzzk_id}-${n.channel_id}`}
            notification={n}
            isSubscription={isSubscription}
            onFeedback={onFeedback}
          />
        ))}
      </tbody>
    </PolicyTable>
  );
}

function ChzzkIdCopyButton({ chzzkId }: { chzzkId: string }) {
  const shortenedId = `${chzzkId.slice(0, 4)}…${chzzkId.slice(-4)}`;

  return (
    <CopyButton
      value={chzzkId}
      label="치지직 채널 ID 복사"
      className="gap-1 w-fit mt-0.5 whitespace-nowrap text-xs font-mono"
      iconClassName="w-3 h-3"
    >
      <span className="md:hidden">{shortenedId}</span>
      <span className="hidden md:inline">{chzzkId}</span>
    </CopyButton>
  );
}

function NotificationRow({
  notification: n,
  isSubscription,
  onFeedback,
}: {
  notification: Notification;
  isSubscription?: boolean;
  onFeedback: (feedback: Feedback) => void;
}) {
  const { test } = useNotificationActions(n.guild_id);

  return (
    <PolicyTr className="group hover:bg-muted/40 transition-colors">
      <PolicyTd className="pl-6 py-4 flex items-center gap-2 whitespace-nowrap">
        <Avatar className="w-10 h-10 border border-border transition-colors">
          <AvatarImage
            src={getChzzkChannelImageUrl(n.chzzk_image_url)}
            alt={n.chzzk_name || n.chzzk_id}
          />
          <AvatarFallback className="bg-primary/20 text-primary text-lg font-semibold">
            {(n.chzzk_name || n.chzzk_id).slice(0, 2)}
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
          <a
            href={getChzzkChannelUrl(n.chzzk_id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 font-medium text-foreground hover:text-primary transition-colors w-fit"
          >
            {n.chzzk_name || "치지직 채널"}
            <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
          </a>
          <ChzzkIdCopyButton chzzkId={n.chzzk_id} />
        </div>
      </PolicyTd>

      <PolicyTd className="whitespace-nowrap">
        <a
          href={getDiscordChannelUrl(n.guild_id, n.channel_id)}
          target="_blank"
          rel="noopener noreferrer"
          title={n.channel_name}
          className="inline-flex max-w-60 items-center gap-1.5 px-2.5 py-1 rounded-md bg-(--blurple)/10 text-(--blurple) text-sm font-medium whitespace-nowrap hover:bg-(--blurple)/20 transition-colors"
          style={{ "--blurple": DISCORD_COLORS.blurple } as CSSProperties}
        >
          <span className="text-xs">#</span>
          <span className="truncate">{n.channel_name || "채널로 이동"}</span>
        </a>
      </PolicyTd>

      <PolicyTd className="whitespace-nowrap">
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
                  ? "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
                  : "bg-rose-500/10 text-rose-400 hover:bg-rose-500/20",
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
            <span className="text-sm">아직 없음</span>
          </div>
        )}
      </PolicyTd>

      <PolicyTd>
        <Button
          size="sm"
          variant="secondary"
          disabled={test.isPending}
          onClick={() =>
            test.mutate(
              {
                guild_id: n.guild_id,
                channel_id: n.channel_id,
                chzzk_id: n.chzzk_id,
              },
              {
                onSuccess: () =>
                  onFeedback({
                    variant: "success",
                    title: `${getNotificationLabel(n)} 테스트 알림을 보냈습니다.`,
                  }),
                onError: (error) =>
                  onFeedback({
                    variant: "destructive",
                    title: `${getNotificationLabel(n)} 테스트 알림을 보내지 못했습니다`,
                    description: getErrorMessage(error),
                    showTestGuide: getErrorMessage(error).includes(
                      "테스트 알림 전송에 실패했습니다",
                    ),
                  }),
              },
            )
          }
        >
          {test.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          테스트 알림 보내기
        </Button>
      </PolicyTd>

      <PolicyTd>
        <EditNotificationDialog
          notification={n}
          isSubscription={isSubscription}
          onFeedback={onFeedback}
        />
      </PolicyTd>

      <PolicyTd>
        <DeleteNotificationDialog notification={n} onFeedback={onFeedback} />
      </PolicyTd>
    </PolicyTr>
  );
}
