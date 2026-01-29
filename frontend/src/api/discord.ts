import { API_ROUTE, ACCESS_TOEKN } from '@/constants';
import { Axios } from '@/lib/Axios';
import { User, Guild } from '@/types';

const { VITE_API_URL } = import.meta.env;

const AuthAxios = new Axios(true, VITE_API_URL, ACCESS_TOEKN);
const unAuthAxios = new Axios(false, VITE_API_URL, ACCESS_TOEKN);

export const login = async (code: string) => {
  const res = await unAuthAxios.post(API_ROUTE.AUTH.LOG_IN, {
    code,
  });

  return res;
};

export const getMe = async () => {
  const res = await AuthAxios.get<User>(API_ROUTE.DISCORD.ME);

  return res;
};

export const getGuilds = async () => {
  const res = await AuthAxios.get<Guild[]>(API_ROUTE.DISCORD.GUILDS);

  return res;
};

export const getChannels = async (guildId: string) => {
  const res = await AuthAxios.get(API_ROUTE.DISCORD.CHANNELS(guildId));

  return res;
};
