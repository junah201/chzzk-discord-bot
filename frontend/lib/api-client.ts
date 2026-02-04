import axios from "axios";
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
