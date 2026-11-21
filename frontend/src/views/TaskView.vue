<script setup lang="ts">
import { type TaskId, tasksApi } from "@/api";
import { computed, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/stores/auth.ts";
import { useTasks } from "@/stores/tasks.ts";
import MarkdownIt from "markdown-it";
import texmath from "markdown-it-texmath";
import katex from "katex";
import "katex/dist/katex.min.css";
import DOMPurify from "dompurify";

const router = useRouter();

const props = defineProps<{
  id: TaskId
}>();

const auth = useAuth();
const tasks = useTasks();

const task = computed(() => tasks.cache[props.id]);

watch(
    () => props.id,
    (id) => tasks.get(id, true),
    { immediate: true }
);

const md = new MarkdownIt({ linkify: true, typographer: true }).use(texmath, {
  engine: katex,
  delimiters: "brackets",
  katexOptions: { output: "html" },
});
const html = computed(
    () => task.value
        ? DOMPurify.sanitize(md.render(task.value.content))
        : ""
);

async function deleteTask() {
  try {
    await tasksApi.remove(props.id);
    tasks.remove(props.id);
    tasks.clear();
  } finally {
    router.replace({ name: 'home' });
  }
}

</script>

<template>
  <template v-if="task">
    <template v-if="task.author.id === auth.user?.id">
      <div class="toolbar">
        <RouterLink class="toolbar-item" :to="{ name: 'taskEdit', params: { id: props.id } }">
          Edytuj
        </RouterLink>
        <button class="toolbar-item" @click="deleteTask">
          Usuń
        </button>
      </div>
    </template>
    <h1>{{ task.title }}</h1>
    <article v-html="html" />
  </template>

</template>

<style scoped>
@reference "@/assets/main.css";

h1 {
  @apply text-2xl font-bold;
}

.toolbar {
  @apply py-3 flex items-stretch;
}

.toolbar .toolbar-item {
  @apply py-1 px-3 mr-2 rounded-md border-none text-black bg-blue-200 hover:bg-blue-300;
}

</style>