import { queryOptions } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Channel, Guild, User } from "@/types/api";

export const keys = {
  all: ["discord"] as const,
  user: () => [...keys.all, "user"] as const,
  guilds: () => [...keys.all, "guilds"] as const,
  guild: (guildId: string | null) => [...keys.guilds(), guildId] as const,
  channels: (guildId: string | null) =>
    [...keys.all, "channels", guildId] as const,
};

export const discordQueries = {
  me: () =>
    queryOptions({
      queryKey: keys.user(),
      queryFn: () => api.get<User>("/discord/me"),
      staleTime: 1000 * 60 * 5,
    }),
  guilds: () =>
    queryOptions({
      queryKey: keys.guilds(),
      queryFn: () => api.get<Guild[]>("/discord/guilds"),
      staleTime: Infinity,
      gcTime: 1000 * 60 * 60,
    }),
  guild: (guildId: string | null) =>
    queryOptions({
      queryKey: keys.guild(guildId),
      queryFn: () => api.get<Guild>(`/discord/${guildId}`),
      enabled: !!guildId,
      staleTime: Infinity,
      gcTime: 1000 * 60 * 60,
    }),
  channels: (guildId: string | null) =>
    queryOptions({
      queryKey: keys.channels(guildId),
      queryFn: () => api.get<Channel[]>(`/discord/${guildId}/channels`),
      enabled: !!guildId,
      staleTime: Infinity,
      gcTime: 1000 * 60 * 60,
    }),
};
