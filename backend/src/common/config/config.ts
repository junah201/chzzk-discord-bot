import type { Config } from './config.interface';

export default (): Config => ({
  aws: {
    region: 'ap-northeast-2',
  },
  discord: {
    apiBaseUrl: 'https://discord.com/api/v10',
    token: process.env.DISCORD_BOT_TOKEN || '',
    clientId: process.env.DISCORD_CLIENT_ID || '',
    clientSecret: process.env.DISCORD_CLIENT_SECRET || '',
    publicKey: process.env.DISCORD_PUBLIC_KEY || '',
  },
  chzzk: {
    apiBaseUrl: 'https://api.chzzk.naver.com/service/v2',
  },
});
