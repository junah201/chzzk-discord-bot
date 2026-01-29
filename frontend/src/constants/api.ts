const AUTH = Object.freeze({
  LOG_IN: '/oauth/token',
});

const DISCORD = Object.freeze({
  ME: '/discord/me',
  GUILDS: '/discord/guilds',
  CHANNELS: (guildId: string) => `/discord/${guildId}/channels`,
});

const NOTIFICATION = Object.freeze({
  ADD: '/notifications',
  UPDATE: '/notifications',
  DELETE: '/notifications',
  SEND_TEST: '/notifications/test',
  GET_BY_GUILD_ID: (guildId: string) => `/notifications/${guildId}`,
});

export const API_ROUTE = Object.freeze({
  AUTH,
  DISCORD,
  NOTIFICATION,
});
