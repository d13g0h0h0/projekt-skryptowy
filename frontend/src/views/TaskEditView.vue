<script setup lang="ts">
import {type SubTask, type Task, type TaskId, tasksApi} from "@/api";
import { useTasks } from "@/stores/tasks.ts";
import {computed, ref, toRaw, watch} from "vue";
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import {useAuth} from "@/stores/auth.ts";
import {ApiError} from "@/api/client.ts";

const props = defineProps<{
  id: TaskId
}>();

const tasks = useTasks();
const auth = useAuth();

const task = computed(() => tasks.cache[props.id]);

watch(
    () => [props.id, auth.user?.id, tasks.cache[props.id]] as const,
    ([id, userId, cached]) => {
      if (userId && !cached)
        tasks.get(id);
    },
    { immediate: true }
);

const draft = ref<Task | null>(null);
const saving = ref<boolean>(false);
const error = ref<string | null>(null);

function clone<T>(value: T): T {
  return structuredClone(toRaw(value));
}

function resetDraft() {
  draft.value = task.value ? clone(task.value) : null;
}

const hasDirtyDraft = computed(
    () => !!draft.value &&
        !!task.value &&
        JSON.stringify(draft.value) !== JSON.stringify(task.value)
);


watch (
    () => [props.id, task.value] as const,
    ([id, t], old) => {
      if (!t) return;
      if (id !== old?.[0] || !draft.value || !hasDirtyDraft.value)
        resetDraft();
    },
    { immediate: true }
);

function addSubtask() {
  draft.value?.subtasks.push({
    id: "0",
    content: "",
  } as SubTask);
}

function removeSubtask(index: number) {
  draft.value?.subtasks.splice(index, 1);
}

async function save() {
  if (!draft.value || saving.value) return;

  saving.value = true;
  error.value = null;
  try {
    const saved = await tasksApi.update(props.id, {
      title: draft.value?.title,
      content: draft.value?.content,
      subtasks: draft.value?.subtasks
    });
    tasks.set(saved);
    resetDraft();
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message;
  } finally {
    saving.value = false;
  }
}

</script>

<template>
  <template v-if="draft">
    <input v-model="draft.title"/>
    <MdEditor class="md-editor" v-model="draft.content" language="en-US"/>
    <div class="subtask-editor" v-for="(subtask, n) in draft.subtasks" :key = subtask.id>
      <button type="button" class="hover:bg-red-500 hover:text-white" @click="removeSubtask(n)">Usuń podzadanie</button>
      <MdEditor v-model="subtask.content" language="en-US"/>
    </div>
    <div class="toolbar">
      <button type="button" @click="addSubtask">Dodaj pozadanie</button>
      <button type="button" :disabled="!hasDirtyDraft || saving" @click="save">
        {{ saving ? "Zapisywanie..." : "Zapisz" }}
      </button>
      <button type="button" class="hover:bg-red-500 hover:text-white" :disabled="!hasDirtyDraft || saving" @click="resetDraft">
        {{ "Odrzuć zmiany" }}
      </button>
    </div>
  </template>
  <p v-else>
    Coś poszło nie tak, nie udało się załadować zadania do edycji.
    <template v-if="error">{{ error }}</template>
  </p>
</template>

<style scoped>
@reference "@/assets/main.css";

input {
  @apply text-2xl font-bold text-black mt-2 mb-2;
}

.md-editor {
  width: 85%;
  max-height: 70vh;
}

.subtask-editor button {
  @apply mt-1 mb-1 px-3 py-1;
}

.toolbar {
  @apply flex items-stretch mt-1 mb-1;
}

.toolbar button {
  @apply px-3 py-1 mr-2 border-none;
}

.subtask-editor button {
  @apply border-none;
}


</style>