<script setup lang="ts">

import type { Task } from "@/api";

const props = defineProps<{
  task: Task
}>();

</script>

<template>
  <div class="box">
    <h3>Autor: {{ props.task.author.username }}</h3>
    <RouterLink :to="{ name: 'task', params: { id: props.task.id } }">
      <h1>{{ props.task.title }}</h1>
    </RouterLink>
    <h3>Ostatnia modyfikacja: {{ (new Date(props.task.updated_at)).toLocaleDateString() }}</h3>
  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

.box {
  @apply min-h-20 border-b-2 border-b-gray-200
}
.box h1 {
  @apply text-xl text-left
}
.box h3 {
  @apply text-sm text-gray-500
}

</style>