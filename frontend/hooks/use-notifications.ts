import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api-client";
import { Notification } from "@/types/api";
import { keys } from "@/queries/notifications";

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
};

export const useNotificationActions = (guildId: string) => {
  const queryClient = useQueryClient();

  const addMutation = useMutation({
    mutationFn: (data: NotificationCreate) =>
      api.post<Notification>(ROUTES.BASE, data),
    onSuccess: () => {
      toast.success("새 알림이 등록되었습니다.");
      queryClient.invalidateQueries({ queryKey: keys.listByGuildId(guildId) });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (data: NotificationBase) => api.delete(ROUTES.BASE, { data }),
    onSuccess: () => {
      toast.success("알림이 삭제되었습니다.");
      queryClient.invalidateQueries({ queryKey: keys.listByGuildId(guildId) });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: NotificationBase) =>
      api.put<Notification>(ROUTES.BASE, data),
    onSuccess: () => {
      toast.success("알림이 수정되었습니다.");
      queryClient.invalidateQueries({ queryKey: keys.listByGuildId(guildId) });
    },
  });

  return {
    add: addMutation,
    remove: deleteMutation,
    update: updateMutation,
  };
};
