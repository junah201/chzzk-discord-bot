"use client";

import { Suspense } from "react";

import { useQuery } from "@tanstack/react-query";
import { discordQueries } from "@/queries/discord";
import ServerHeaderSkeleton from "./components/server-header-skeleton";
import ServerHeader from "./components/server-header";
import { useSearchParams } from "next/navigation";

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

  const { data: serverData, isLoading: isServerLoading } = useQuery(
    discordQueries.guild(serverId),
  );

  return (
    <>
      {isServerLoading ? (
        <ServerHeaderSkeleton />
      ) : (
        <ServerHeader server={serverData!} />
      )}
    </>
  );
}
