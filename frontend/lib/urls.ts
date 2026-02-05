export const getChzzkChannelUrl = (chzzkId: string) => {
  return `https://chzzk.naver.com/${chzzkId}`;
};

export const getChzzkLiveUrl = (chzzkId: string) => {
  return `https://chzzk.naver.com/live/${chzzkId}`;
};

export const getDiscordChannelUrl = (guildId: string, channelId: string) => {
  return `https://discord.com/channels/${guildId}/${channelId}`;
};

export const getDiscordIconUrl = (
  serverId: string,
  iconHash: string | null | undefined,
  size: 64 | 128 | 256 | 512 = 64,
) => {
  if (!iconHash) return undefined;
  return `https://cdn.discordapp.com/icons/${serverId}/${iconHash}.webp?size=${size}`;
};
