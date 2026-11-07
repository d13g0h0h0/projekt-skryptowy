<script setup lang="ts">
withDefaults(defineProps<{
  text?: string;
  spinnerColor?: string;
}>(), {
  text: "Loading...",
  spinnerColor: "brick"
});
</script>

<template>
  <div class="w-full min-h-[220px] flex flex-col justify-center items-center gap-3">
    <span class="w-10 h-10 border-[color:var(--color-border)] animate-spin rounded-full border-[0.3rem] border-solid" :style="{ borderTopColor: spinnerColor }"></span>
    <p>{{ text }}</p>
  </div>
</template>

<style scoped>

p {
  font-size: 1rem;
}





</style>