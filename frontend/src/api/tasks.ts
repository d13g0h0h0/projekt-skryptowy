import { requestTask, requestTaskList } from "@/api/client.ts";

export const tasksApi = {
  list: () => requestTaskList(),
  get: (id: string) => requestTask(id)
};