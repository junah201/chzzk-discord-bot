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

interface DeleteNotificationDialogProps {
  notification: Notification;
}

export default function DeleteNotificationDialog({
  notification,
}: DeleteNotificationDialogProps) {
  const [open, setOpen] = useState(false);
  const { remove } = useNotificationActions(notification.guild_id);
  const chzzkId =
    notification.chzzk_id || notification.PK.split("#")[1] || "unknown";

  const handleDelete = () => {
    remove.mutate(
      {
        guild_id: notification.guild_id,
        channel_id: notification.channel_id,
        chzzk_id: chzzkId,
      },
      {
        onSuccess: () => setOpen(false),
      },
    );
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
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
          <AlertDialogTitle>알림 설정을 삭제하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            <span className="font-semibold text-foreground">
              {notification.channel_name || chzzkId}
            </span>{" "}
            채널의 알림 설정이 영구적으로 삭제됩니다.
            <br />이 작업은 되돌릴 수 없습니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
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
            삭제 확인
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
