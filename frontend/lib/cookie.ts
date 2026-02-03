import Cookies from "js-cookie";

const isProd = process.env.NODE_ENV === "production";

export const setCookie = (
  key: string,
  value: string,
  options?: Cookies.CookieAttributes,
): void => {
  Cookies.set(key, value, {
    path: "/",
    secure: isProd,
    sameSite: isProd ? "strict" : "lax",
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
