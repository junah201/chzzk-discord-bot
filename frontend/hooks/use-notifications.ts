import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Guild, Notification } from "@/types/api";
import { keys as notificationKeys } from "@/queries/notifications";
import { keys as discordKeys } from "@/queries/discord";
import { sendGAEvent } from "@next/third-parties/google";

interface NotificationBase {
  guild_id: string;
  channel_id: string;
  chzzk_id: string;
}

interface NotificationSettings extends NotificationBase {
  custom_message: string;
  webhook_url?: string;
  embed_color?: string;
  disable_embed: boolean;
  disable_tag: boolean;
  disable_button: boolean;
  disable_notification: boolean;
}

const ROUTES = {
  BASE: "/notifications",
  LIST: (guildId: string) => `/notifications/${guildId}`,
  TEST: "/notifications/test",
};

const INLINE_ERROR = { inlineError: true };

export const useNotificationActions = (guildId: string) => {
  const queryClient = useQueryClient();

  const addMutation = useMutation({
    meta: INLINE_ERROR,
    mutationFn: (data: NotificationSettings) =>
      api.post<Notification>(ROUTES.BASE, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: notificationKeys.listByGuildId(guildId),
      });
      queryClient.setQueryData<Guild>(discordKeys.guild(guildId), (oldData) => {
        if (!oldData) return oldData;

        return {
          ...oldData,
          current_count: (oldData.current_count || 0) + 1,
        };
      });

      sendGAEvent("event", "create_notification", {
        guild_id: guildId,
        chzzk_id: variables.chzzk_id,
        channel_id: variables.channel_id,
      });
    },
  });

  const deleteMutation = useMutation({
    meta: INLINE_ERROR,
    mutationFn: (data: NotificationBase) => api.delete(ROUTES.BASE, { data }),
    onSuccess: (_, variables) => {
      queryClient.setQueryData<Notification[]>(
        notificationKeys.listByGuildId(guildId),
        (oldData) => {
          if (!oldData) return oldData;

          return oldData.filter(
            (item) =>
              !(
                item.chzzk_id === variables.chzzk_id &&
                item.channel_id === variables.channel_id
              ),
          );
        },
      );
      queryClient.setQueryData<Guild>(discordKeys.guild(guildId), (oldData) => {
        if (!oldData) return oldData;

        return {
          ...oldData,
          current_count: Math.max(0, (oldData.current_count || 0) - 1),
        };
      });

      sendGAEvent("event", "delete_notification", {
        guild_id: guildId,
        chzzk_id: variables.chzzk_id,
        channel_id: variables.channel_id,
      });
    },
  });

  const updateMutation = useMutation({
    meta: INLINE_ERROR,
    mutationFn: (data: NotificationSettings) =>
      api.put<Notification>(ROUTES.BASE, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: notificationKeys.listByGuildId(guildId),
      });

      sendGAEvent("event", "update_notification", {
        guild_id: guildId,
        chzzk_id: variables.chzzk_id,
        channel_id: variables.channel_id,
      });
    },
  });

  const testMutation = useMutation({
    meta: INLINE_ERROR,
    mutationFn: (data: NotificationBase) => api.post(ROUTES.TEST, data),
    onSuccess: (_, variables) => {
      sendGAEvent("event", "test_notification", {
        guild_id: guildId,
        chzzk_id: variables.chzzk_id,
        channel_id: variables.channel_id,
        result: "success",
      });
    },
    onError: (_, variables) => {
      sendGAEvent("event", "test_notification", {
        guild_id: guildId,
        chzzk_id: variables.chzzk_id,
        channel_id: variables.channel_id,
        result: "fail",
      });
    },
  });

  return {
    add: addMutation,
    remove: deleteMutation,
    update: updateMutation,
    test: testMutation,
  };
};
