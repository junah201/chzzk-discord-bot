import { queryOptions } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Guild, User } from "@/types/api";

const keys = {
  all: ["discord"] as const,
  user: () => [...keys.all, "user"] as const,
  guilds: () => [...keys.all, "guilds"] as const,
  channels: (guildId: string) => [...keys.all, "channels", guildId] as const,
};

export const discordQueries = {
  me: () =>
    queryOptions({
      queryKey: keys.user(),
      queryFn: () => apiClient.get<User>("/discord/me"),
      staleTime: 1000 * 60 * 5,
    }),

  // 길드 목록
  guilds: () =>
    queryOptions({
      queryKey: keys.guilds(),
      queryFn: () => apiClient.get<Guild[]>("/discord/guilds"),
    }),

  // 채널 목록 (파라미터 받는 경우)
  channels: (guildId: string) =>
    queryOptions({
      queryKey: keys.channels(guildId),
      queryFn: () => apiClient.get(`/discord/${guildId}/channels`),
      enabled: !!guildId,
    }),
};
