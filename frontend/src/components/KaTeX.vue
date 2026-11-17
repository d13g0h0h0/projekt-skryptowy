<script setup lang="ts">

import {computed} from "vue";
import katex from "katex";

const props = defineProps({
  expression: { type: String, required: true },
  displayMode: { type: Boolean, required: false },
});

const html = computed(() =>
    katex.renderToString(props.expression, {
      displayMode: props.displayMode,
      throwOnError: false,
    })
);

</script>

<template>
  <span v-html="html"></span>
</template>

<style scoped>

</style>