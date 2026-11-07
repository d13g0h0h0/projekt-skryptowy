<script setup lang="ts">
import { type Task, tasksApi } from '@/api';
import { onMounted, ref } from "vue";
import TaskTile from "@/components/TaskTile.vue";
import LoadingCircle from "@/components/LoadingCircle.vue";

const tasks = ref<Task[]>([]);
const is_loading = ref<boolean>(true);

onMounted(async () => {
  tasks.value = await tasksApi.list();
  is_loading.value = false;
});
</script>

<template>
  <h1>Nasze zadanka</h1>
  <main>
    <LoadingCircle v-if="is_loading"/>
    <TaskTile v-else v-for="task in tasks" :task="task" :key="task.id"/>
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