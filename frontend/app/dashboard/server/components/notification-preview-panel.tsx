"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { Control, useWatch } from "react-hook-form";
import { BellOff, Eye } from "lucide-react";

import { NotificationPreview } from "@/components/discord/notification-preview";
import { DEFAULT_EMBED_COLOR, parseEmbedColor } from "@/lib/discord";
import { discordQueries } from "@/queries/discord";
import { NotificationFormValues } from "./notification-form";
import { ServerContext } from "../server-context";

interface NotificationPreviewPanelProps {
  control: Control<NotificationFormValues>;
  chzzkName?: string;
  chzzkImageUrl?: string;
}

/** 폼 입력을 그대로 반영하는 디스코드 알림 미리보기 */
export default function NotificationPreviewPanel({
  control,
  chzzkName,
  chzzkImageUrl,
}: NotificationPreviewPanelProps) {
  const { serverId, isSubscription } = use(ServerContext);
  const values = useWatch({ control });
  const { data: channels = [] } = useQuery(discordQueries.channels(serverId));

  const channelNames = Object.fromEntries(
    channels.map((channel) => [channel.id, channel.name]),
  );
  const channelName = values.channel_id
    ? channelNames[values.channel_id]
    : undefined;
  // 백엔드도 구독 중이고 웹훅 URL이 있을 때만 웹훅으로 보냄
  const usesWebhook = isSubscription && Boolean(values.webhook_url?.trim());
  const embedColor =
    (isSubscription && parseEmbedColor(values.embed_color ?? "")) ||
    DEFAULT_EMBED_COLOR;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
        <Eye className="size-4" />
        미리보기
        {channelName && (
          <span className="truncate text-xs text-muted-foreground/70">
            · #{channelName}
          </span>
        )}
      </div>

      <div className="relative overflow-hidden rounded-lg border border-border">
        <NotificationPreview
          className={values.disable_notification ? "opacity-40" : undefined}
          content={values.custom_message ?? ""}
          embedColor={embedColor}
          disableEmbed={values.disable_embed}
          disableTag={values.disable_tag}
          disableButton={values.disable_button}
          channelNames={channelNames}
          customSender={usesWebhook}
          live={{
            channelName: chzzkName || "스트리머",
            channelImageUrl: chzzkImageUrl,
            title: "방송 제목이 여기에 표시됩니다",
            category: "카테고리",
            tags: ["방송 태그", "예시"],
          }}
        />
        {values.disable_notification && (
          <div className="absolute inset-0 flex items-center justify-center p-6">
            <p className="flex items-center gap-2 rounded-md bg-background/90 px-3 py-2 text-sm font-medium shadow">
              <BellOff className="size-4 text-muted-foreground" />
              알림이 일시 중지되어 전송되지 않습니다
            </p>
          </div>
        )}
      </div>

      <p className="text-xs text-muted-foreground/70">
        방송 제목, 카테고리, 태그, 썸네일은 실제 방송 정보로 채워집니다.
        {usesWebhook &&
          " 커스텀 웹훅으로 보내므로 이름과 프로필 이미지는 웹훅에 설정한 값으로 표시됩니다."}
      </p>
    </div>
  );
}
