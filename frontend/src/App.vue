<script setup lang="ts">
</script>

<template>
  <nav>
    <RouterLink to="/">Home</RouterLink> |
  </nav>
  <div id="view">
    <RouterView />
  </div>
</template>

<style scoped>
@reference "@/assets/main.css";

header {
  line-height: 1.5;
}

nav {
  @apply bg-blue-200
}

nav a {
  @apply text-black
}

#view {
  padding: 0 2rem;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>