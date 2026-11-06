import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { keys as discordKeys } from "@/queries/discord";
import { Guild, SlotSyncResult } from "@/types/api";

export const useSyncSlots = (guildId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    meta: { inlineError: true },
    mutationFn: () =>
      api.post<SlotSyncResult>(`/discord/${guildId}/slots/sync`),
    onSuccess: ({ current_count, max_limit }) => {
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
    },
  });
};
