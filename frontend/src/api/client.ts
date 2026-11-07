import type { Task } from "./types.ts";

const BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}/api${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.status === 204 ? (undefined as T) : res.json()
}

export async function requestTaskList(): Promise<Task[]> {
  const response = await fetch("/sample_tasks.json");
  return await response.json();
}

export async function requestTask(id: string): Promise<Task | void> {
  const all_tasks = await requestTaskList();
  for (const task of all_tasks) {
    if (task.id === id) return task;
  }
}