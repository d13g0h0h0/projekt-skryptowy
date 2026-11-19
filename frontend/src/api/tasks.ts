import { request } from "./client.ts";
import {type Task, type TaskId, type CreateTaskInput, type Solution, type CreateSolutionInput} from "./types.ts"

const endpoint = "/api/tasks/";

export const tasksApi = {
  list: (signal?: AbortSignal) =>
    request<Task[]>(endpoint, { signal }),

  create: (input: CreateTaskInput) =>
    request<Task>(endpoint, { method: 'POST', body: input }),

  get: (id: TaskId, signal?: AbortSignal) =>
    request<Task>(`${endpoint}${id}`, { signal }),

  update: (id: TaskId, input: CreateTaskInput) =>
    request<Task>(`${endpoint}${id}/`, { method: 'PUT', body: input }),

  remove: (id: TaskId) =>
    request<void>(`${endpoint}${id}`, { method: 'DELETE' }),

  get_solutions: (id: TaskId, signal?: AbortSignal) =>
    request<Solution[]>(`${endpoint}${id}/solutions/`, { method: 'GET', signal }),

  create_solution: (id: TaskId, input: CreateSolutionInput) =>
    request<Solution>(`${endpoint}${id}/solutions/`, { method: 'POST', body: input }),
};