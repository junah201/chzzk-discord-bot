"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import routeMap from "@/constants/route-map";
import { isAxiosError } from "axios";
import { discordQueries } from "@/queries/discord";
import BotMissingPage from "./bot-missing";
import UnknownErrorPage from "./unknown-error";
import { APIError } from "@/types/api";
import AdminRequiredPage from "./admin-required";
import { useGuildOptions } from "@/hooks/use-guild-options";
import RateLimitedPage from "./rate-limited";

interface ServerBotGuardProps {
  children: React.ReactNode;
}

export default function ServerBotGuard({ children }: ServerBotGuardProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const serverId = searchParams.get("id");

  useEffect(() => {
    if (!serverId) {
      router.replace(routeMap.DASHBOARD.HOME);
    }
  }, [serverId, router]);

  const { isError: isChannelError, error: channelError } = useQuery(
    discordQueries.channels(serverId),
  );

  const { isError: isGuildError, error: guildError } = useQuery(
    useGuildOptions(serverId),
  );

  const getErrorCode = (error: unknown) => {
    return isAxiosError<APIError>(error) ? error.response?.data?.code : null;
  };

  const channelErrorCode = isChannelError ? getErrorCode(channelError) : null;
  const guildErrorCode = isGuildError ? getErrorCode(guildError) : null;

  if (
    channelErrorCode === "BOT_NOT_JOINED" ||
    guildErrorCode === "BOT_NOT_JOINED"
  )
    return <BotMissingPage />;

  if (
    channelErrorCode === "USER_NOT_ADMIN" ||
    guildErrorCode === "USER_NOT_ADMIN"
  )
    return <AdminRequiredPage />;

  if (channelErrorCode === "RATE_LIMITED" || guildErrorCode === "RATE_LIMITED")
    return <RateLimitedPage />;

  if (isChannelError) return <UnknownErrorPage error={channelError} />;
  if (isGuildError) return <UnknownErrorPage error={guildError} />;

  return <>{children}</>;
}
