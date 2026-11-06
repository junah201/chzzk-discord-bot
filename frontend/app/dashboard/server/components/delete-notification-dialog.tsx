"use client";

import { useState } from "react";
import { Trash2, Loader2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { useNotificationActions } from "@/hooks/use-notifications";
import { Notification } from "@/types/api";
import MutationAlert, {
  Feedback,
  getNotificationLabel,
} from "./mutation-alert";

interface DeleteNotificationDialogProps {
  notification: Notification;
  onFeedback?: (feedback: Feedback) => void;
}

export default function DeleteNotificationDialog({
  notification,
  onFeedback,
}: DeleteNotificationDialogProps) {
  const [open, setOpen] = useState(false);
  const { remove } = useNotificationActions(notification.guild_id);
  const chzzkId =
    notification.chzzk_id || notification.PK.split("#")[1] || "unknown";

  const handleDelete = () => {
    // 삭제되면 이 행이 언마운트되어 mutate 콜백이 실행되지 않으므로 promise로 처리
    remove
      .mutateAsync({
        guild_id: notification.guild_id,
        channel_id: notification.channel_id,
        chzzk_id: chzzkId,
      })
      .then(() => {
        setOpen(false);
        onFeedback?.({
          variant: "success",
          title: `${getNotificationLabel(notification)} 알림을 삭제했습니다.`,
        });
      })
      .catch(() => {});
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (nextOpen) {
      remove.reset();
    }
    setOpen(nextOpen);
  };

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogTrigger asChild>
        <Button
          size="sm"
          variant="outline"
          className="h-8 gap-1.5 border-rose-500/20 text-rose-600 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-500/30"
        >
          {remove.isPending ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Trash2 className="w-3.5 h-3.5" />
          )}
          <span className="text-xs font-medium">삭제</span>
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>이 알림을 삭제할까요?</AlertDialogTitle>
          <AlertDialogDescription>
            <span className="font-semibold text-foreground">
              {notification.chzzk_name || chzzkId}
            </span>{" "}
            채널의{" "}
            <span className="font-semibold text-foreground">
              #{notification.channel_name || notification.channel_id}
            </span>{" "}
            알림 설정이 영구적으로 삭제됩니다.
            <br />이 작업은 되돌릴 수 없습니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <MutationAlert
          error={remove.error}
          errorTitle="알림을 삭제하지 못했습니다"
          onClose={remove.reset}
        />
        <AlertDialogFooter>
          <AlertDialogCancel disabled={remove.isPending}>
            취소
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault();
              handleDelete();
            }}
            disabled={remove.isPending}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {remove.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            삭제
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
