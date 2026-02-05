"use client";

import { useState } from "react";
import { Edit2, Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useNotificationActions } from "@/hooks/use-notifications";
import { Notification } from "@/types/api";
import NotificationForm from "./notification-form";

interface EditNotificationDialogProps {
  notification: Notification;
}

export default function EditNotificationDialog({
  notification,
}: EditNotificationDialogProps) {
  const [open, setOpen] = useState(false);
  const { update } = useNotificationActions(notification.guild_id);
  const chzzkId =
    notification.chzzk_id || notification.PK.split("#")[1] || "unknown";

  const { control, handleSubmit, reset } = useForm({
    defaultValues: {
      chzzk_id: chzzkId,
      channel_id: notification.channel_id,
      guild_id: notification.guild_id,
      custom_message: notification.custom_message || "",
      disable_embed: notification.disable_embed || false,
      disable_button: notification.disable_button || false,
      disable_notification: notification.disable_notification || false,
    },
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          size="sm"
          variant="outline"
          className="h-8 gap-1.5 hover:bg-secondary hover:text-foreground"
        >
          {update.isPending ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Edit2 className="w-3.5 h-3.5" />
          )}
          <span className="text-xs font-medium">수정</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>알림 설정 수정</DialogTitle>
          <DialogDescription>저장된 알림 설정을 변경합니다.</DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <NotificationForm
            serverId={notification.guild_id}
            control={control}
            isEdit
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={update.isPending}
          >
            취소
          </Button>
          <Button
            onClick={handleSubmit((data) =>
              update.mutate(data, {
                onSuccess: () => {
                  setOpen(false);
                  reset(data);
                },
              }),
            )}
            disabled={update.isPending}
          >
            {update.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            변경사항 저장
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
