/**
 * Zustand store for authentication state.
 *
 * Per .cursorrules specification (lines 176-177).
 * Centralizes auth state management with persistence.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AuthState } from '@/types/auth';

interface AuthActions {
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      setUser: (user) => {
        const isAuthenticated = user !== null;
        // Sync cookie with auth state
        if (typeof document !== 'undefined') {
          if (isAuthenticated) {
            document.cookie = 'pulse-auth=true; path=/; max-age=2592000';
          } else {
            document.cookie = 'pulse-auth=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          }
        }
        set({ user, isAuthenticated });
      },

      setToken: (token) =>
        set({ token }),

      setLoading: (isLoading) =>
        set({ isLoading }),

      login: (user, token) => {
        // Set cookie for middleware to check auth status
        if (typeof document !== 'undefined') {
          document.cookie = 'pulse-auth=true; path=/; max-age=2592000'; // 30 days
        }
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () => {
        // Clear cookie when logging out
        if (typeof document !== 'undefined') {
          document.cookie = 'pulse-auth=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        }
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },
    }),
    {
      name: 'pulse-auth-storage', // localStorage key
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Sync cookie with rehydrated auth state
        if (state && typeof document !== 'undefined') {
          if (state.isAuthenticated) {
            document.cookie = 'pulse-auth=true; path=/; max-age=2592000';
          } else {
            document.cookie = 'pulse-auth=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          }
        }
      },
    }
  )
);
