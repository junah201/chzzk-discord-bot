"use client";

import { Input } from "@/components/input";
import routeMap from "@/constants/route-map";

import { discordQueries } from "@/queries/discord";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Control } from "react-hook-form";

export interface NotificationFormValues {
  chzzk_id: string;
  channel_id: string;
  guild_id: string;
  custom_message: string;
  webhook_url: string;
  embed_color: string;
  disable_embed: boolean;
  disable_tag: boolean;
  disable_button: boolean;
  disable_notification: boolean;
}

interface NotificationFormProps {
  serverId: string;
  control: Control<NotificationFormValues>;
  isEdit?: boolean;
  isSubscription?: boolean;
}

export default function NotificationForm({
  serverId,
  control,
  isEdit = false,
  isSubscription = false,
}: NotificationFormProps) {
  const { data } = useQuery(discordQueries.channels(serverId));
  const channels = data || [];

  return (
    <div className="flex flex-col gap-4">
      {!isEdit && (
        <>
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
            disabled={isEdit}
          />
          <Input
            type="select"
            control={control}
            name="channel_id"
            label="디스코드 채널"
            rules={{ required: "알림을 받을 디스코드 채널을 선택해 주세요." }}
            helperText={
              <>
                새로 만든 채널이 보이지 않으면 페이지를
                <a
                  href=""
                  onClick={() => location.reload()}
                  className="underline hover:text-primary/80 mx-1"
                >
                  새로고침
                </a>
                해 주세요.
              </>
            }
            options={channels.map((channel) => ({
              label: `#${channel.name}`,
              value: channel.id,
            }))}
            disabled={isEdit}
          />
        </>
      )}
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
      <Input
        type="text"
        control={control}
        name="webhook_url"
        label="커스텀 웹훅 URL (구독자 전용)"
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
        label="임베드 색상 (구독자 전용)"
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
