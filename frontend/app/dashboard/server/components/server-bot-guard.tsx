"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { discordQueries } from "@/queries/discord";
import BotMissingPage from "./bot-missing";
import UnknownErrorPage from "./unknown-error";
import { getErrorCode } from "@/lib/api-error";
import AdminRequiredPage from "./admin-required";
import { useGuildOptions } from "@/hooks/use-guild-options";
import RateLimitedPage from "./rate-limited";
import { ServerContext } from "../server-context";

interface ServerBotGuardProps {
  children: React.ReactNode;
}

export default function ServerBotGuard({ children }: ServerBotGuardProps) {
  const { serverId } = use(ServerContext);
  const { isError: isChannelError, error: channelError } = useQuery(
    discordQueries.channels(serverId),
  );

  const { isError: isGuildError, error: guildError } = useQuery(
    useGuildOptions(serverId),
  );

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
