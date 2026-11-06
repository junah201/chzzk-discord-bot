import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { keys as discordKeys } from "@/queries/discord";
import { Guild, SlotSyncResult } from "@/types/api";

export const useSyncSlots = (guildId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      api.post<SlotSyncResult>(`/discord/${guildId}/slots/sync`),
    onSuccess: ({ current_count, previous_count, max_limit }) => {
      const withResult = (guild: Guild): Guild => ({
        ...guild,
        current_count,
        max_limit,
      });

      queryClient.setQueryData<Guild>(discordKeys.guild(guildId), (oldData) =>
        oldData ? withResult(oldData) : oldData,
      );
      queryClient.setQueryData<Guild[]>(discordKeys.guilds(), (oldData) =>
        oldData?.map((guild) =>
          guild.id === guildId ? withResult(guild) : guild,
        ),
      );

      if (current_count === previous_count) {
        toast.success("슬롯 개수가 이미 실제 알림 수와 같습니다.");
      } else {
        toast.success(
          `사용 중인 슬롯을 ${previous_count}개에서 ${current_count}개로 갱신했습니다.`,
        );
      }
    },
  });
};
