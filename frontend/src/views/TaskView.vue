<script setup lang="ts">

import { type Task, tasksApi } from "@/api";
import { onMounted, ref } from "vue";

const props = defineProps<{
  id: string
}>();

const task = ref<Task>();
const is_loading = ref<boolean>(true);

onMounted(async () => {
  task.value = (await tasksApi.get(props.id))!;
  is_loading.value = false;
});

</script>

<template>
  <template v-if="task">
    <h1>{{ task.title }}</h1>
    <p>{{ task.content }}</p>
  </template>

</template>

<style scoped>
@reference "@/assets/main.css";

h1 {
  @apply text-2xl font-bold
}

</style>