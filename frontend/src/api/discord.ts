import { API_ROUTE, ACCESS_TOEKN } from '@/constants';
import { Axios } from '@/lib/Axios';

const { VITE_API_URL } = import.meta.env;

const unAuthAxios = new Axios(false, VITE_API_URL, ACCESS_TOEKN);

export const login = async (code: string) => {
  const res = await unAuthAxios.post(API_ROUTE.AUTH.LOG_IN, {
    code,
  });

  return res;
};
