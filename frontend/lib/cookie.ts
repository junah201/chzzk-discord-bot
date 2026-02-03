import { IS_PROD } from "@/constants/env";
import Cookies from "js-cookie";

export const setCookie = (
  key: string,
  value: string,
  options?: Cookies.CookieAttributes,
): void => {
  Cookies.set(key, value, {
    path: "/",
    secure: IS_PROD,
    sameSite: IS_PROD ? "strict" : "lax",
    ...options,
  });
};

export const getCookie = (key: string): string | undefined => {
  return Cookies.get(key);
};

export const removeCookie = (
  key: string,
  options?: Cookies.CookieAttributes,
): void => {
  Cookies.remove(key, {
    path: "/",
    ...options,
  });
};
