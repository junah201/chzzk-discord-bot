"use client";

import { use } from "react";
import { Input } from "@/components/input";
import routeMap from "@/constants/route-map";

import { discordQueries, keys } from "@/queries/discord";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Control, useWatch } from "react-hook-form";
import SubscriberSection from "./subscriber-section";
import { ServerContext } from "../server-context";

export interface NotificationFormValues {
  chzzk_id: string;
  channel_id: string;
  guild_id: string;
  custom_message: string;
  webhook_url: string;
  embed_color: string;
  auto_crosspost: boolean;
  disable_embed: boolean;
  disable_tag: boolean;
  disable_button: boolean;
  disable_notification: boolean;
}

const GUILD_ANNOUNCEMENT_CHANNEL = 5;

interface NotificationFieldsProps {
  control: Control<NotificationFormValues>;
}

export function NotificationTargetFields({ control }: NotificationFieldsProps) {
  const { serverId } = use(ServerContext);
  const queryClient = useQueryClient();
  const { data, isFetching } = useQuery(discordQueries.channels(serverId));
  const channels = data || [];

  return (
    <div className="flex flex-col gap-4">
      <Input
        type="text"
        control={control}
        name="chzzk_id"
        label="치지직 ID"
        placeholder="bb382c2c0cc9fa7c86"
        rules={{ required: "치지직 ID를 입력해 주세요." }}
        helperText={
          <>
            치지직 ID를 찾는 방법은{" "}
            <Link href={routeMap.DOCS.NOTIFICATIONS}>알림 등록 문서</Link>를
            참고하세요.
          </>
        }
      />
      <Input
        type="select"
        control={control}
        name="channel_id"
        label="디스코드 채널"
        rules={{ required: "알림을 받을 디스코드 채널을 선택해 주세요." }}
        helperText={
          <>
            새로 만든 채널이 보이지 않으면 채널 목록을
            <button
              type="button"
              onClick={() =>
                queryClient.invalidateQueries({
                  queryKey: keys.channels(serverId),
                })
              }
              disabled={isFetching}
              className="underline hover:text-primary/80 mx-1 disabled:opacity-50 disabled:cursor-wait"
            >
              {isFetching ? "불러오는 중" : "새로고침"}
            </button>
            해 주세요.
          </>
        }
        options={channels.map((channel) => ({
          label: `#${channel.name}`,
          value: channel.id,
        }))}
        isLoading={isFetching}
      />
    </div>
  );
}

export function NotificationSettingsFields({
  control,
}: NotificationFieldsProps) {
  const { serverId, isSubscription } = use(ServerContext);
  const { data: channels } = useQuery(discordQueries.channels(serverId));
  const [channelId, autoCrosspost] = useWatch({
    control,
    name: ["channel_id", "auto_crosspost"],
  });
  const channel = channels?.find((c) => c.id === channelId);
  const isAnnouncement = channel?.type === GUILD_ANNOUNCEMENT_CHANNEL;

  return (
    <div className="flex flex-col gap-4">
      <Input
        type="textarea"
        control={control}
        name="custom_message"
        label="커스텀 메시지"
        placeholder="@everyone 새로운 방송이 시작되었습니다! 시청하러 가볼까요?"
        helperText={
          <>
            멘션을 넣는 방법은{" "}
            <Link href={routeMap.DOCS.CUSTOMIZATION}>메시지 커스텀 문서</Link>를
            참고하세요.
          </>
        }
      />
      <SubscriberSection locked={!isSubscription}>
        <Input
          type="text"
          control={control}
          name="webhook_url"
          label="커스텀 웹훅 URL"
          disabled={!isSubscription}
          placeholder="https://discord.com/api/webhooks/..."
          helperText={
            <>
              치직 봇 대신 웹훅에 설정한 이름과 프로필 이미지로 알림을 보냅니다.
              설정 방법은{" "}
              <Link
                href={routeMap.DOCS.CUSTOM_WEBHOOK}
                className="underline hover:text-primary/80"
              >
                커스텀 웹훅 문서
              </Link>
              를 참고하세요.
            </>
          }
        />
        <Input
          type="color"
          control={control}
          name="embed_color"
          label="임베드 색상"
          disabled={!isSubscription}
          rules={{
            pattern: {
              value: /^#[0-9a-fA-F]{6}$/,
              message: "5865F2 같은 6자리 색상 코드로 입력해 주세요.",
            },
          }}
          helperText="임베드 왼쪽 띠의 색입니다. 구독이 끝나면 기본 색상으로 돌아갑니다."
        />
        <Input
          type="checkbox"
          control={control}
          name="auto_crosspost"
          label="공지 채널 자동 게시"
          // 켜 둔 상태에서는 구독이 끝났거나 채널을 바꿨어도 끌 수 있게 둔다.
          disabled={!autoCrosspost && (!isSubscription || !isAnnouncement)}
          rules={{
            validate: (value) =>
              !value ||
              !channel ||
              isAnnouncement ||
              "공지 채널에서만 자동 게시를 사용할 수 있습니다.",
          }}
          helperText={
            <>
              방송 알림을 보내면 바로 게시해서 이 공지 채널을 팔로우한 서버에도
              전달합니다. 공지 채널에서만 사용할 수 있고, 커스텀 웹훅을 쓰면
              봇에 메시지 관리 권한이 필요합니다. 자세한 내용은{" "}
              <Link
                href={routeMap.DOCS.AUTO_CROSSPOST}
                className="underline hover:text-primary/80"
              >
                자동 게시 문서
              </Link>
              를 참고하세요.
            </>
          }
        />
      </SubscriberSection>
      <Input
        type="checkbox"
        control={control}
        name="disable_embed"
        label="임베드 숨기기"
        helperText="방송 제목과 썸네일이 담긴 임베드 없이 메시지만 보냅니다."
      />
      <Input
        type="checkbox"
        control={control}
        name="disable_tag"
        label="방송 태그 숨기기"
        helperText="임베드에 방송 태그를 표시하지 않습니다."
      />
      <Input
        type="checkbox"
        control={control}
        name="disable_button"
        label="바로가기 버튼 숨기기"
        helperText="알림 아래의 바로가기 버튼을 표시하지 않습니다."
      />
      <Input
        type="checkbox"
        control={control}
        name="disable_notification"
        label="알림 일시 중지"
        helperText="이 알림을 보내지 않습니다. 설정은 그대로 남아 있습니다."
      />
    </div>
  );
}
