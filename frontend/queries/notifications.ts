import { queryOptions } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Notification } from "@/types/api";

export const keys = {
  all: ["notifications"] as const,
  listByGuildId: (guildId: string) => [...keys.all, "list", guildId] as const,
};

export const notificationQueries = {
  listByGuildId: (guildId: string) =>
    queryOptions({
      queryKey: keys.listByGuildId(guildId),
      queryFn: () => api.get<Notification[]>(`/notifications/${guildId}`),
      staleTime: 1000 * 60 * 5,
    }),
};
