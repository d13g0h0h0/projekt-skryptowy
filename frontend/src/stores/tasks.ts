import { defineStore } from "pinia";
import { type Task, type TaskId, tasksApi } from "@/api";
import {ref, watch} from "vue";
import {useAuth} from "@/stores/auth.ts";

export const useTasks = defineStore("task", () => {
  const cache = ref<Record<TaskId, Task>>({});

  let generation = 0;

  async function get(id: TaskId, force = false): Promise<Task> {
    if (!force && cache.value[id])
      return cache.value[id];
    const gen = generation
    const task = await tasksApi.get(id);
    if (gen === generation)
      cache.value[id] = task;
    return task;
  }

  function set(task: Task) {
    cache.value[task.id] = task;
  }



  function clear() {
    generation++;
    cache.value = {};
  }

  const auth = useAuth();

  watch(
    () => auth.user?.id,
    clear
  );

  return { cache, get, set, clear };
});