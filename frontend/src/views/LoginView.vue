<script setup lang="ts">
import { ref } from "vue";
import type { LoginInput } from "@/api";
import { useRoute, useRouter } from "vue-router";
import { ApiError } from "@/api/client.ts";
import { useAuth } from "@/stores/auth.ts";

const router = useRouter();
const route = useRoute();
const auth = useAuth();

const loginInput = ref<LoginInput>({ password: "", username: "" });
const error = ref<string>("");
const loading = ref<boolean>(false);

function getRedirect() : string {
  const raw = Array.isArray(route.query.redirect)
      ? route.query.redirect[0]
      : route.query.redirect;
  if (typeof raw === "string" && raw.startsWith("/") && !raw.startsWith("//")) {
    return raw;
  }
  return "/";
}

async function submit() {
  if (loading.value) return;
  
  error.value = "";
  loading.value = true;
  try {
    await auth.login(loginInput.value);
    router.replace(getRedirect());
  }
  catch (e) {
    if (e instanceof ApiError && (e.status === 400 || e.status === 401)) {
      error.value = "Niepoprawna nazwa użytkownika lub hasło";
    }
    else {
      error.value = "Coś poszło nie tak, spróbuj jeszcze raz";
    }
  }
  finally {
    loading.value = false;
  }
}


</script>

<template>
  <form @submit.prevent="submit">
    <input v-model="loginInput.username" placeholder="Nazwa użytkownika" autocomplete="username" :disabled="loading" />
    <input v-model="loginInput.password" type="password" placeholder="Hasło" autocomplete="current-password" :disabled="loading" />
    <button :disabled="loading">{{ loading ? "Logowanie..." : "Zaloguj" }}</button>
    <p v-if="error">{{ error }}</p>
  </form>
</template>

<style scoped>
@reference "@/assets/main.css";

form {
  @apply flex flex-col max-w-xs items-start;
}

form button {
  @apply px-3 py-1;
}

form > * {
  @apply mt-3;
}

</style>