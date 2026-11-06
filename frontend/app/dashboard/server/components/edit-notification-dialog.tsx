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
import { toHexEmbedColor } from "@/lib/discord";
import { Notification } from "@/types/api";
import NotificationForm from "./notification-form";
import NotificationPreviewPanel from "./notification-preview-panel";
import MutationAlert, {
  Feedback,
  getNotificationLabel,
} from "./mutation-alert";

interface EditNotificationDialogProps {
  notification: Notification;
  onFeedback?: (feedback: Feedback) => void;
}

export default function EditNotificationDialog({
  notification,
  onFeedback,
}: EditNotificationDialogProps) {
  const [open, setOpen] = useState(false);
  const { update } = useNotificationActions(notification.guild_id);

  const getDefaultValues = () => ({
    chzzk_id: notification.chzzk_id,
    channel_id: notification.channel_id,
    guild_id: notification.guild_id,
    custom_message: notification.custom_message || "",
    webhook_url: notification.webhook_url || "",
    embed_color: toHexEmbedColor(notification.embed_color || ""),
    disable_embed: notification.disable_embed || false,
    disable_tag: notification.disable_tag || false,
    disable_button: notification.disable_button || false,
    disable_notification: notification.disable_notification || false,
  });

  const { control, handleSubmit, reset } = useForm({
    defaultValues: getDefaultValues(),
  });

  // 열 때마다 저장된 설정으로 되돌려, 취소한 입력이 남지 않게 함
  const handleOpenChange = (nextOpen: boolean) => {
    if (nextOpen) {
      reset(getDefaultValues());
      update.reset();
    }
    setOpen(nextOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
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
      <DialogContent className="@container max-h-[90vh] overflow-y-auto sm:max-w-2xl lg:max-w-6xl">
        <DialogHeader>
          <DialogTitle>알림 설정 수정</DialogTitle>
          <DialogDescription>저장된 알림 설정을 변경합니다.</DialogDescription>
        </DialogHeader>

        <div className="grid gap-8 py-4 @5xl:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
          <NotificationForm control={control} isEdit />
          <div className="@5xl:sticky @5xl:top-0 @5xl:self-start">
            <NotificationPreviewPanel
              control={control}
              chzzkName={notification.chzzk_name}
              chzzkImageUrl={notification.chzzk_image_url}
            />
          </div>
        </div>

        <MutationAlert
          error={update.error}
          errorTitle="알림 설정을 저장하지 못했습니다"
          onClose={update.reset}
        />

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
                  onFeedback?.({
                    variant: "success",
                    title: `${getNotificationLabel(notification)} 알림을 수정했습니다.`,
                  });
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
