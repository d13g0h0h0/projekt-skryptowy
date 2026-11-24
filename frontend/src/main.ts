import './assets/main.css';

import { createApp } from 'vue';
import App from './App.vue';
import router from "@/router";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();

  app
    .use(pinia)
    .use(router)
    .use(PrimeVue, { theme: { preset: Aura } });

  await router.isReady();

  app.mount("#app");
}

bootstrap();
