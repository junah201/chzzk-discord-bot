"use client";

import { motion } from "motion/react";
import NotificationForm from "./notification-form";
import NotificationPreviewPanel from "./notification-preview-panel";
import { Card, CardContent } from "@/components/ui/card";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { useNotificationActions } from "@/hooks/use-notifications";
import { Loader2, Plus } from "lucide-react";

interface AddNotificationFormProps {
  serverId: string;
  isSubscription?: boolean;
}

export default function AddNotificationForm({
  serverId,
  isSubscription = false,
}: AddNotificationFormProps) {
  const { add } = useNotificationActions(serverId);
  const { control, handleSubmit, reset } = useForm({
    defaultValues: {
      chzzk_id: "",
      channel_id: "",
      guild_id: serverId,
      custom_message: "",
      webhook_url: "",
      embed_color: "",
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
      <Card className="bg-card border-border transition-all duration-300 group hover:border-primary/50 h-full flex flex-col z-10 @container">
        <CardContent className="grid gap-8 @5xl:grid-cols-[minmax(0,1fr)_minmax(0,26rem)]">
          <div className="flex flex-col gap-4">
            <NotificationForm
              serverId={serverId}
              control={control}
              isSubscription={isSubscription}
            />
            <Button
              onClick={handleSubmit((data) =>
                add.mutate(data, {
                  onSuccess: () => {
                    reset();
                  },
                }),
              )}
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
          </div>
          <div className="@5xl:sticky @5xl:top-6 @5xl:self-start">
            <NotificationPreviewPanel
              serverId={serverId}
              control={control}
              isSubscription={isSubscription}
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
