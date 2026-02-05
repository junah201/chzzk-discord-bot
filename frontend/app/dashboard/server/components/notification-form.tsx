"use client";

import { Input } from "@/components/input";
import routeMap from "@/constants/route-map";

import { discordQueries } from "@/queries/discord";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Control } from "react-hook-form";

interface NotificationFormProps {
  serverId: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  control: Control<any>;
  isEdit?: boolean;
}

export default function NotificationForm({
  serverId,
  control,
  isEdit = false,
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
            rules={{ required: "치지직 채널의 고유 ID를 입력해주세요" }}
            helperText={
              <>
                치지직 ID를 찾는 방법은{" "}
                <Link href={routeMap.DOCS.NOTIFICATIONS}>방송 알림 문서</Link>를
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
            rules={{ required: "디스코드 채널을 선택해주세요" }}
            helperText={
              <>
                새롭게 추가한 채널이 목록에 보이지 않는다면, 페이지를
                <a
                  href=""
                  onClick={() => location.reload()}
                  className="underline hover:text-primary/80 mx-1"
                >
                  새로고침
                </a>
                해보세요
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
            역할 멘션 등 자세한 설정 방법은{" "}
            <Link href={routeMap.DOCS.CUSTOMIZATION}>메시지 커스텀 문서</Link>를
            참고하세요
          </>
        }
      />
      <Input
        type="checkbox"
        control={control}
        name="disable_embed"
        label="임베드 비활성화"
        helperText="방송 알림 임베드를 비활성화합니다"
      />
      <Input
        type="checkbox"
        control={control}
        name="disable_button"
        label="바로가기 버튼 비활성화"
        helperText="방송 알림의 바로가기 버튼을 비활성화합니다"
      />
      <Input
        type="checkbox"
        control={control}
        name="disable_notification"
        label="알림 비활성화"
        helperText="방송 알림의 알림 기능을 비활성화합니다"
      />
    </div>
  );
}
