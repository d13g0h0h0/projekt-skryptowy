<script setup lang="ts">
import { type Task, tasksApi } from '@/api';
import { ref, watch } from "vue";
import TaskTile from "@/components/TaskTile.vue";
import LoadingCircle from "@/components/LoadingCircle.vue";
import { useAuth } from "@/stores/auth.ts";

const auth = useAuth();

const tasks = ref<Task[]>([]);
const isLoading = ref<boolean>(true);
const error = ref<string | null>(null);

let requestId = 0;

watch (
    () => auth.isLoggedIn,
    async (isLoggedIn) => {
      const currentRequest = ++requestId;

      tasks.value = [];
      error.value = null;

      if (!isLoggedIn) {
        isLoading.value = false;
        return;
      }

      isLoading.value = true;

      try {
        const result = await tasksApi.list();
        if (currentRequest === requestId) {
          tasks.value = result;
        }
      } catch {
        if (currentRequest === requestId) {
          error.value = "Nie udało się pobrać zadań.";
        }
      } finally {
        if (currentRequest === requestId) {
          isLoading.value = false;
        }
      }
    },
    { immediate: true }
)
</script>

<template>
  <h1>Nasze zadanka</h1>
  <main>
    <LoadingCircle v-if="isLoading"/>
    <p v-else-if="!auth.isLoggedIn">
      Zaloguj się, aby zobaczyć zadania.
    </p>
    <p v-else-if="error">{{ error }}</p>
    <template v-else>
      <TaskTile v-for="task in tasks" :task="task" :key="task.id"/>
      <p v-if="!tasks.length">Brak zadań.</p>
    </template>
  </main>
</template>

<style scoped>
@reference "@/assets/main.css";

h1 {
  @apply text-2xl font-bold text-black
}

main {
  @apply flex-col content-stretch border-t-2 border-t-gray-200
}
</style>