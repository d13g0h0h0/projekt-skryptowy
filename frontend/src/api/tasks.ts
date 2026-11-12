import { request } from "./client.ts";
import { type Task, type CreateTaskInput } from "./types.ts"

const endpoint = "/api/tasks/";

export const tasksApi = {
  list: (signal?: AbortSignal) =>
    request<Task[]>(endpoint, { signal }),

  get: (id: string, signal?: AbortSignal) =>
    request<Task>(`${endpoint}${id}`, { signal }),

  create: (input: CreateTaskInput) =>
    request<Task>(endpoint, { method: 'POST', body: input }),

  update: (id: string, input: CreateTaskInput) =>
    request<Task>(`${endpoint}${id}`, { method: 'PUT', body: input }),

  remove: (id: string) =>
    request<void>(`${endpoint}${id}`, { method: 'DELETE' }),
};