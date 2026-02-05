import axios, { AxiosRequestConfig } from "axios";
import { ACCESS_TOKEN } from "@/constants/cookies";
import { getCookie } from "@/lib/cookie";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getCookie(ACCESS_TOKEN.key);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error),
);

export const api = {
  get: <T>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T, T>(url, config),

  post: <T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig) =>
    apiClient.post<T, T, D>(url, data, config),

  put: <T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig) =>
    apiClient.put<T, T, D>(url, data, config),

  delete: <T>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T, T>(url, config),
};
