<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import type { RegisterInput } from "@/api";
import { ApiError } from "@/api/client.ts";
import { useAuth } from "@/stores/auth.ts";

const router = useRouter();
const auth = useAuth();

const registerInput = ref<RegisterInput>({ username: "", email: "", password: "", role: "student" });
const pendingApproval = ref<boolean>(false);
const passwordRepeat = ref<string>("");
const fieldErrors = ref<Record<string, string[]>>({});
const generalError = ref<string>("");
const loading = ref<boolean>(false);

async function submit() {
  if (loading.value) return;

  fieldErrors.value = {};
  generalError.value = "";

  if (registerInput.value.password !== passwordRepeat.value) {
    generalError.value = "Hasła się nie zgadzają";
    return;
  }

  loading.value = true;
  try {
    const isLoggedIn = await auth.register(registerInput.value);
    if (isLoggedIn) {
      router.replace({ name: "home" });
    } else {
      pendingApproval.value = true;
    }
  }
  catch (requestError) {
    if (requestError instanceof ApiError && requestError.status === 400 && requestError.body) {
      fieldErrors.value = requestError.body as Record<string, string[]>;
    }
    else {
      generalError.value = "Coś poszło nie tak, spróbuj jeszcze raz";
    }
  }
  finally {
    loading.value = false;
  }
}
</script>

<template>
  <div v-if="pendingApproval" class="notice">
    Konto nauczyciela zostało utworzone i czeka na akceptację administratora.
    Zalogujesz się, gdy zostanie zatwierdzone.
  </div>
  <form v-else @submit.prevent="submit">
    <input v-model="registerInput.username" placeholder="Nazwa użytkownika" autocomplete="username" :disabled="loading" />
    <p v-for="message in fieldErrors.username" :key="message" class="error">{{ message }}</p>

    <input v-model="registerInput.email" type="email" placeholder="E-mail" autocomplete="email" :disabled="loading" />
    <p v-for="message in fieldErrors.email" :key="message" class="error">{{ message }}</p>

    <input v-model="registerInput.password" type="password" placeholder="Hasło" autocomplete="new-password" :disabled="loading" />
    <p v-for="message in fieldErrors.password" :key="message" class="error">{{ message }}</p>

    <input v-model="passwordRepeat" type="password" placeholder="Powtórz hasło" autocomplete="new-password" :disabled="loading" />

    <fieldset :disabled="loading">
      <legend>Rejestruję się jako:</legend>
      <label><input v-model="registerInput.role" type="radio" value="student" /> Student</label>
      <label><input v-model="registerInput.role" type="radio" value="teacher" /> Nauczyciel</label>
    </fieldset>
    <p v-if="registerInput.role === 'teacher'" class="hint">
      Konto nauczyciela wymaga akceptacji administratora.
    </p>

    <button :disabled="loading">{{ loading ? "Rejestracja..." : "Zarejestruj" }}</button>
    <p v-if="generalError" class="error">{{ generalError }}</p>

    <RouterLink to="/login">Masz już konto? Zaloguj się</RouterLink>
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
.error {
  @apply text-sm text-red-600 mt-1;
}
.notice {
  @apply mt-6 p-3 bg-yellow-100 border border-yellow-400 max-w-md;
}
.hint {
  @apply text-sm text-gray-500 mt-1;
}
fieldset {
  @apply flex gap-4 border-0 p-0;
}
</style>