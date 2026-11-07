"use client";

import { use } from "react";
import { motion } from "motion/react";
import {
  NotificationSettingsFields,
  NotificationTargetFields,
} from "./notification-form";
import NotificationPreviewPanel from "./notification-preview-panel";
import MutationAlert from "./mutation-alert";
import { Card, CardContent } from "@/components/ui/card";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { useNotificationActions } from "@/hooks/use-notifications";
import { Loader2, Plus } from "lucide-react";
import { ServerContext } from "../server-context";

export default function AddNotificationForm() {
  const { serverId } = use(ServerContext);
  const { add } = useNotificationActions(serverId);
  const { control, handleSubmit, reset } = useForm({
    defaultValues: {
      chzzk_id: "",
      channel_id: "",
      guild_id: serverId,
      custom_message: "",
      webhook_url: "",
      embed_color: "",
      auto_crosspost: false,
      disable_embed: false,
      disable_tag: false,
      disable_button: false,
      disable_notification: false,
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05, duration: 0.4 }}
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <h2 className="text-2xl font-bold">알림 추가</h2>
          <p className="text-sm text-muted-foreground mt-1">
            치지직 채널과 알림을 받을 디스코드 채널을 등록합니다.
          </p>
        </div>
      </div>
      <Card className="bg-card border-border h-full flex flex-col z-10 @container">
        <CardContent className="grid grid-cols-[minmax(0,1fr)] gap-8 @5xl:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
          <form
            noValidate
            onSubmit={handleSubmit((data) =>
              add.mutate(data, {
                onSuccess: () => {
                  reset();
                },
              }),
            )}
            className="flex flex-col gap-4"
          >
            <NotificationTargetFields control={control} />
            <NotificationSettingsFields control={control} />
            <MutationAlert
              error={add.error}
              isSuccess={add.isSuccess}
              errorTitle="알림을 추가하지 못했습니다"
              successMessage="새 알림이 등록되었습니다."
              onClose={add.reset}
            />
            <Button
              type="submit"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={add.isPending}
            >
              {add.isPending ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Plus className="w-3.5 h-3.5" />
              )}
              알림 추가
            </Button>
          </form>
          <div className="@5xl:sticky @5xl:top-6 @5xl:self-start">
            <NotificationPreviewPanel control={control} />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
