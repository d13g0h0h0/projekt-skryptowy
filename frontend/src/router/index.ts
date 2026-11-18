import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import {useAuth} from "@/stores/auth.ts";

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/task/:id',
    name: 'task',
    component: () => import('@/views/TaskView.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

/**
 * Ensures that logged-out users don't access views with `meta.requiresAuth`,
 * and that logged-in users don't get sent to `login`.
 */
router.beforeEach(async (to) => {
  const auth = useAuth();
  await auth.initialize();

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: "login", query: { redirect: to.fullPath } };
  }

  if (to.name === "login" && auth.isLoggedIn) {
    return { name: "home" };
  }
});

export default router;