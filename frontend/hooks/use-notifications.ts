import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
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

interface NotificationCreate extends NotificationBase {
  custom_message: string;
}

const ROUTES = {
  BASE: "/notifications",
  LIST: (guildId: string) => `/notifications/${guildId}`,
  TEST: "/notifications/test",
};

export const useNotificationActions = (guildId: string) => {
  const queryClient = useQueryClient();

  const addMutation = useMutation({
    mutationFn: (data: NotificationCreate) =>
      api.post<Notification>(ROUTES.BASE, data),
    onSuccess: (_, variables) => {
      toast.success("새 알림이 등록되었습니다.");
      queryClient.invalidateQueries({
        queryKey: notificationKeys.listByGuildId(guildId),
      });
      queryClient.setQueryData(discordKeys.guild(guildId), (oldData: Guild) => {
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
    mutationFn: (data: NotificationBase) => api.delete(ROUTES.BASE, { data }),
    onSuccess: (_, variables) => {
      toast.success("알림이 삭제되었습니다.");
      queryClient.setQueryData(
        notificationKeys.listByGuildId(guildId),
        (oldData: Notification[]) => {
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
      queryClient.setQueryData(discordKeys.guild(guildId), (oldData: Guild) => {
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
    mutationFn: (data: NotificationBase) =>
      api.put<Notification>(ROUTES.BASE, data),
    onSuccess: (_, variables) => {
      toast.success("알림이 수정되었습니다.");
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
    mutationFn: (data: NotificationBase) => api.post(ROUTES.TEST, data),
    onSuccess: (_, variables) => {
      toast.success("테스트 알림이 전송되었습니다.");

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
