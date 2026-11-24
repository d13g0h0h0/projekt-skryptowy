import { defineStore } from "pinia";
import {authApi, type LoginInput, type RegisterInput, type User} from "@/api";

interface AuthState {
  user: User | null,
  initialized: boolean,
}

export const useAuth = defineStore("auth", {
  state: () : AuthState => ({
    user: null,
    initialized: false,
  }),

  getters: {
    isLoggedIn: (s) : boolean => !!s.user,
  },

  actions: {
    async initialize() {
      if (this.initialized) return;

      try {
        this.user = await authApi.me();
      } catch {
        this.user = null;
      } finally {
        this.initialized = true;
      }
    },

    async login(input: LoginInput) {
      await authApi.login(input);
      this.user = await authApi.me();
      this.initialized = true;
    },

    async logout() {
      try {
        await authApi.logout();
      }
      finally {
        this.user = null;
        this.initialized = true;
      }
    },

    async register(input: RegisterInput) {
      this.user = await authApi.register(input);
      this.initialized = true;
    },
  }
});