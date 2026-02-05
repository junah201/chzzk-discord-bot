import { api } from "@/lib/api-client";

interface LoginResponse {
  token_type: string;
  access_token: string;
  expires_in: number;
  refresh_token: string;
  scope: string;
}

export const authMutations = {
  login: (code: string) => api.post<LoginResponse>("/oauth/token", { code }),
};
