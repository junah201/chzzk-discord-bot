import type { Config } from './config.interface';

const config: Config = {
  aws: {
    region: 'ap-northeast-2',
  },
  discord: {
    apiBaseUrl: 'https://discord.com/api/v10',
    token: (() => {
      if (!process.env.DISCORD_BOT_TOKEN) {
        throw new Error(
          'DISCORD_BOT_TOKEN is not defined in environment variables',
        );
      }
      return process.env.DISCORD_BOT_TOKEN;
    })(),
  },
} as const;

export default (): Config => config;
