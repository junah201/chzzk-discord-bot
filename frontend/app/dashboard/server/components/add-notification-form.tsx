"use client";

import { motion } from "motion/react";
import NotificationForm from "./notification-form";
import { Card, CardContent } from "@/components/ui/card";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { useNotificationActions } from "@/hooks/use-notifications";

interface AddNotificationFormProps {
  serverId: string;
}

export default function AddNotificationForm({
  serverId,
}: AddNotificationFormProps) {
  const { add } = useNotificationActions(serverId);
  const { control, handleSubmit, reset } = useForm({
    defaultValues: {
      chzzk_id: "",
      channel_id: "",
      guild_id: serverId,
      custom_message: "",
      disable_embed: false,
      disable_button: false,
      disable_notification: false,
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <h2 className="text-2xl font-bold">알림 추가</h2>
          <p className="text-sm text-muted-foreground mt-1">
            새로운 치지직 채널의 방송 알림을 설정하세요
          </p>
        </div>
      </div>
      <Card className="bg-card border-border transition-all duration-300 group hover:border-primary/50 h-full flex flex-col z-10">
        <CardContent className="flex flex-col gap-4">
          <NotificationForm serverId={serverId} control={control} />
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
          >
            알림 추가
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}
