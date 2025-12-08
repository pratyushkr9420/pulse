/**
 * Tests for LoginForm component.
 *
 * Tests integration with useAuth hook and authStore.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginForm } from '@/components/auth/LoginForm';
import { useAuthStore } from '@/stores/authStore';

// Mock Next.js router
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

// Mock apiClient - use vi.hoisted to ensure mocks are available before imports
const { mockLogin } = vi.hoisted(() => ({
  mockLogin: vi.fn(),
}));

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    login: mockLogin,
    register: vi.fn(),
    getMe: vi.fn(),
    getChatHistory: vi.fn(),
    sendMessage: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset auth store
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  afterEach(() => {
    useAuthStore.getState().logout();
  });

  it('renders login form', () => {
    render(<LoginForm />, { wrapper: createWrapper() });

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('submits form and calls API', async () => {
    const user = userEvent.setup();

    // Mock successful login via apiClient
    mockLogin.mockResolvedValueOnce({
      token: {
        access_token: 'test-token',
        token_type: 'bearer',
      },
      user: {
        id: 'user-1',
        username: 'testuser',
        created_at: new Date().toISOString(),
      },
    });

    render(<LoginForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('updates auth store on successful login', async () => {
    const user = userEvent.setup();

    mockLogin.mockResolvedValueOnce({
      token: {
        access_token: 'test-token',
        token_type: 'bearer',
      },
      user: {
        id: 'user-1',
        username: 'testuser',
        created_at: new Date().toISOString(),
      },
    });

    render(<LoginForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      const authState = useAuthStore.getState();
      expect(authState.isAuthenticated).toBe(true);
      expect(authState.token).toBe('test-token');
    });
  });

  it('navigates to /chat on successful login', async () => {
    const user = userEvent.setup();

    mockLogin.mockResolvedValueOnce({
      token: {
        access_token: 'test-token',
        token_type: 'bearer',
      },
      user: {
        id: 'user-1',
        username: 'testuser',
        created_at: new Date().toISOString(),
      },
    });

    render(<LoginForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/chat');
    });
  });

  it('handles login errors', async () => {
    const user = userEvent.setup();
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

    render(<LoginForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'wronguser');
    await user.type(screen.getByLabelText(/password/i), 'wrongpass');
    await user.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Login failed:',
        expect.any(Error)
      );
    });

    expect(mockPush).not.toHaveBeenCalled();

    const authState = useAuthStore.getState();
    expect(authState.isAuthenticated).toBe(false);

    consoleErrorSpy.mockRestore();
  });
});
