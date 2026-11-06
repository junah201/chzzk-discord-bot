"use client";

import { createContext } from "react";

export interface ServerContextValue {
  serverId: string;
  isSubscription: boolean;
}

export const ServerContext = createContext<ServerContextValue>({
  serverId: "",
  isSubscription: false,
});

export const ServerProvider = ServerContext;
