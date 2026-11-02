"use client";

import { Suspense } from "react";

import { useQuery } from "@tanstack/react-query";
import ServerHeaderSkeleton from "./components/server-header-skeleton";
import ServerHeader from "./components/server-header";
import { useSearchParams } from "next/navigation";
import AddNotificationForm from "./components/add-notification-form";
import { useGuildOptions } from "@/hooks/use-guild-options";
import SetupGuideCallout from "./components/setup-guide-callout";
import NotificationManager from "./components/notification-manager";
import TestGuideCallout from "./components/test-guide-callout";
import ServerBotGuard from "./components/server-bot-guard";
import NotificationLimitCard from "./components/notification-limit-card";
import {
  DEFAULT_SLOT_LIMIT,
  SUBSCRIPTION_SLOT_LIMIT,
} from "@/constants/slots";

export default function ServerDetailPage() {
  return (
    <Suspense>
      <ClientServerDetailPage />
    </Suspense>
  );
}

function ClientServerDetailPage() {
  const searchParams = useSearchParams();
  const serverId = searchParams.get("id");

  const { data: serverData } = useQuery(
    useGuildOptions(serverId),
  );

  const isSubscription = serverData?.max_limit === SUBSCRIPTION_SLOT_LIMIT;

  return (
    <ServerBotGuard>
      {serverData ? (
        <ServerHeader server={serverData} />
      ) : (
        <ServerHeaderSkeleton />
      )}
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <NotificationLimitCard
          currentCount={serverData?.current_count || 0}
          maxLimit={serverData?.max_limit || DEFAULT_SLOT_LIMIT}
        />
      </div>
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <AddNotificationForm
          serverId={serverId!}
          isSubscription={isSubscription}
        />
        <SetupGuideCallout />
      </div>
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 pb-6">
        <NotificationManager
          serverId={serverId!}
          isSubscription={isSubscription}
        />
        <TestGuideCallout />
      </div>
    </ServerBotGuard>
  );
}
