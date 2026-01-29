import { Cookies } from 'react-cookie';

const cookies = new Cookies();

export const setCookie = (key: string, value: string, option: object): void => {
  return cookies.set(key, value, {
    path: '/',
    ...option,
  });
};

export const getCookie = (key: string): any => {
  return cookies.get(key);
};

export const removeCookie = (key: string): void => {
  return cookies.remove(key);
};
