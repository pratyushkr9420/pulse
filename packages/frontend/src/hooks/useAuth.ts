/**
 * useAuth hook - Authentication state and operations.
 *
 * Per .cursorrules specification (lines 170-173).
 * Encapsulates auth logic using authStore.
 */

import { useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { apiClient } from '@/lib/api-client';
import type { LoginRequest, RegisterRequest } from '@/types/auth';

export function useAuth() {
  const { user, token, isAuthenticated, isLoading, login, logout, setLoading } =
    useAuthStore();

  const loginUser = useCallback(
    async (credentials: LoginRequest) => {
      setLoading(true);
      try {
        // Use apiClient for centralized backend calls
        const { token: tokenData, user: userData } = await apiClient.login(credentials);

        // Update store
        login(userData, tokenData.access_token);
      } catch (error) {
        setLoading(false);
        throw error;
      }
    },
    [login, setLoading]
  );

  const registerUser = useCallback(
    async (data: RegisterRequest) => {
      setLoading(true);
      try {
        // Use apiClient for centralized backend calls
        await apiClient.register(data);

        // After registration, log the user in
        await loginUser({ username: data.username, password: data.password });
      } catch (error) {
        setLoading(false);
        throw error;
      }
    },
    [loginUser, setLoading]
  );

  const logoutUser = useCallback(() => {
    logout();
  }, [logout]);

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    login: loginUser,
    register: registerUser,
    logout: logoutUser,
  };
}
