import { request } from "./client.ts";
import type { LoginInput, RegisterInput, User } from "./types.ts";

const endpoint = "/api/auth/";

export const authApi = {
  login: (input: LoginInput) =>
    request<User>(`${endpoint}login/`, { method: 'POST', body: input }),

  logout: () =>
    request<void>(`${endpoint}logout/`, { method: 'POST' }),

  register: (input: RegisterInput) =>
    request<User>(`${endpoint}register/`, { method: 'POST', body: input }),

  me: () =>
    request<User>(`${endpoint}me/`, { method: 'GET' }),
}