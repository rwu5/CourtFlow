import { http } from "./client";
import type { TokenResponse, User } from "../types";

export async function loginWithPhone(
  phone: string,
  code: string,
): Promise<TokenResponse> {
  return http.post<TokenResponse>(
    "/api/v1/auth/phone-login",
    { phone, code },
    false,
  );
}

export async function refreshToken(
  refresh_token: string,
): Promise<TokenResponse> {
  return http.post<TokenResponse>(
    "/api/v1/auth/refresh",
    { refresh_token },
    false,
  );
}

export async function getMe(): Promise<User> {
  return http.get<User>("/api/v1/users/me");
}

export async function updateMe(
  data: Partial<User>,
): Promise<User> {
  return http.put<User>("/api/v1/users/me", data as Record<string, unknown>);
}
