import './assets/main.css';

import { createApp } from 'vue';
import App from './App.vue';
import router from "@/router";
import { createPinia } from "pinia";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();

  app
    .use(pinia)
    .use(router);

  await router.isReady();

  app.mount("#app");
}

bootstrap();
