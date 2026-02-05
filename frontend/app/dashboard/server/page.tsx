"use client";

import { Suspense } from "react";

import { useQuery } from "@tanstack/react-query";
import ServerHeaderSkeleton from "./components/server-header-skeleton";
import ServerHeader from "./components/server-header";
import { useSearchParams } from "next/navigation";
import { useGuildOptions } from "@/hooks/use-guild-options";

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
    useGuildOptions(serverId),
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
