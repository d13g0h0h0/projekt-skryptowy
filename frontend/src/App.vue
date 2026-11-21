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
 * Logs out the user. Activates the router if the current view has `meta.requiresAuth` and redirects first to `LoginView.vue`.
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
    <RouterLink class="nav-item" to="/">Home</RouterLink>
    <template v-if="auth.isLoggedIn">
      <button class="nav-item" @click="seed_task()">
        Zaseeduj taski
      </button>
      <button class="nav-item" @click="logout">
        Wyloguj ({{ auth.user?.username }})
      </button>
    </template>
    <template v-else>
      <RouterLink class="nav-item" to="/login">
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
  @apply bg-blue-200 flex items-stretch;
}

nav button {
  @apply border-0 bg-transparent rounded-none;
}

nav .nav-item {
  @apply px-3 py-1 border-r-2 border-r-gray-600 items-center text-black;
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