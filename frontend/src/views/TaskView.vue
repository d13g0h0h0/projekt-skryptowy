<script setup lang="ts">
import { type TaskId } from "@/api";
import {computed, watch} from "vue";
import { useAuth } from "@/stores/auth.ts";
import {useTasks} from "@/stores/tasks.ts";
import MarkdownIt from "markdown-it";
import texmath from "markdown-it-texmath";
import katex from "katex";
import "katex/dist/katex.min.css";
import DOMPurify from "dompurify";

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



</script>

<template>
  <template v-if="task">
    <RouterLink v-if="task.author.id === auth.user?.id" :to="{ name: 'task_edit', params: { id: props.id } }">
      Edytuj
    </RouterLink>
    <h1>{{ task.title }}</h1>
    <article v-html="html" />
  </template>

</template>

<style scoped>
@reference "@/assets/main.css";

h1 {
  @apply text-2xl font-bold
}

</style>