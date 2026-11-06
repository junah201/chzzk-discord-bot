"use client";

import { Suspense, useEffect } from "react";

import { useQuery } from "@tanstack/react-query";
import ServerHeaderSkeleton from "./components/server-header-skeleton";
import ServerHeader from "./components/server-header";
import { useRouter, useSearchParams } from "next/navigation";
import routeMap from "@/constants/route-map";
import AddNotificationForm from "./components/add-notification-form";
import { useGuildOptions } from "@/hooks/use-guild-options";
import NotificationManager from "./components/notification-manager";
import ServerBotGuard from "./components/server-bot-guard";
import NotificationLimitCard from "./components/notification-limit-card";
import { DEFAULT_SLOT_LIMIT, SUBSCRIPTION_SLOT_LIMIT } from "@/constants/slots";

export default function ServerDetailPage() {
  return (
    <Suspense>
      <ClientServerDetailPage />
    </Suspense>
  );
}

function ClientServerDetailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const serverId = searchParams.get("id");

  useEffect(() => {
    if (!serverId) {
      router.replace(routeMap.DASHBOARD.HOME);
    }
  }, [serverId, router]);

  if (!serverId) return null;

  return <ServerDetail serverId={serverId} />;
}

function ServerDetail({ serverId }: { serverId: string }) {
  const { data: serverData } = useQuery(useGuildOptions(serverId));

  const isSubscription = serverData?.max_limit === SUBSCRIPTION_SLOT_LIMIT;

  return (
    <ServerBotGuard serverId={serverId}>
      {serverData ? (
        <ServerHeader server={serverData} />
      ) : (
        <ServerHeaderSkeleton />
      )}
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <NotificationLimitCard
          serverId={serverId}
          currentCount={serverData?.current_count || 0}
          maxLimit={serverData?.max_limit || DEFAULT_SLOT_LIMIT}
        />
      </div>
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <AddNotificationForm
          serverId={serverId}
          isSubscription={isSubscription}
        />
      </div>
      <div className="relative container mx-auto px-4 sm:px-6 lg:px-8 pb-6">
        <NotificationManager
          serverId={serverId}
          isSubscription={isSubscription}
        />
      </div>
    </ServerBotGuard>
  );
}
