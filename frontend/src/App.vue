<script setup lang="ts">
import { tasksApi } from "@/api";
import { useAuth } from "@/stores/auth.ts";
import { useRouter } from "vue-router";
function seed_task() {
  tasksApi.create({"title": "Pierwsze zadanie", "content": "Treść pierwszego zadania.", "subtasks": []});
}

const auth = useAuth();
const router = useRouter();

/**
 * Logs out the user. Activates the router if the current view has `meta.requiresAuth`.
 */
async function logout() {
  try {
    await auth.logout();
  } finally {
    if (router.currentRoute.value.meta.requiresAuth) {
      router.replace({ name: "login", query: { redirect: router.currentRoute.value.fullPath } });
    }
  }
}

</script>

<template>
  <nav>
    <RouterLink to="/">Home</RouterLink>
    <template v-if="auth.isLoggedIn">
      |
      <button @click="seed_task()">
        Zaseeduj taski
      </button>
      |
      <button @click="logout">
        Wyloguj ({{ auth.user?.username }})
      </button>
    </template>
    <template v-else>
      |
      <RouterLink to="/login">
        Zaloguj
      </RouterLink>
    </template>
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