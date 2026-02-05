import { discordQueries, keys } from "@/queries/discord";
import { Guild } from "@/types/api";
import { queryOptions, useQueryClient } from "@tanstack/react-query";

export const useGuildOptions = (guildId: string | null) => {
  const queryClient = useQueryClient();
  const baseOptions = discordQueries.guild(guildId);

  return queryOptions({
    ...baseOptions,
    initialData: () =>
      queryClient
        .getQueryData<Guild[]>(keys.guilds())
        ?.find((g) => g.id === guildId),
    initialDataUpdatedAt: () =>
      queryClient.getQueryState(keys.guilds())?.dataUpdatedAt,
  });
};
