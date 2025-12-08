/**
 * Tests for RegisterForm component.
 *
 * Tests integration with useAuth hook and authStore.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RegisterForm } from '@/components/auth/RegisterForm';
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
const { mockRegister, mockLogin } = vi.hoisted(() => ({
  mockRegister: vi.fn(),
  mockLogin: vi.fn(),
}));

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    login: mockLogin,
    register: mockRegister,
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

describe('RegisterForm', () => {
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

  it('renders register form', () => {
    render(<RegisterForm />, { wrapper: createWrapper() });

    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getAllByLabelText(/password/i)[0]).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  it('submits form with matching passwords', async () => {
    const user = userEvent.setup();

    // Mock successful registration
    mockRegister.mockResolvedValueOnce(undefined);

    // Mock successful login after registration
    mockLogin.mockResolvedValueOnce({
      token: {
        access_token: 'test-token',
        token_type: 'bearer',
      },
      user: {
        id: 'user-1',
        username: 'newuser',
        created_at: new Date().toISOString(),
      },
    });

    render(<RegisterForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'newuser');
    await user.type(screen.getAllByLabelText(/password/i)[0], 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        username: 'newuser',
        password: 'password123',
      });
    });
  });

  it('does not submit when passwords do not match', async () => {
    const user = userEvent.setup();
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<RegisterForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'newuser');
    await user.type(screen.getAllByLabelText(/password/i)[0], 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'differentpassword');
    await user.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith('Passwords do not match');
    });

    expect(mockRegister).not.toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });

  it('updates auth store on successful registration', async () => {
    const user = userEvent.setup();

    // Mock successful registration
    mockRegister.mockResolvedValueOnce(undefined);

    // Mock successful login
    mockLogin.mockResolvedValueOnce({
      token: {
        access_token: 'test-token',
        token_type: 'bearer',
      },
      user: {
        id: 'user-1',
        username: 'newuser',
        created_at: new Date().toISOString(),
      },
    });

    render(<RegisterForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'newuser');
    await user.type(screen.getAllByLabelText(/password/i)[0], 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      const authState = useAuthStore.getState();
      expect(authState.isAuthenticated).toBe(true);
      expect(authState.token).toBe('test-token');
    });
  });

  it('navigates to /chat on successful registration', async () => {
    const user = userEvent.setup();

    // Mock successful registration
    mockRegister.mockResolvedValueOnce(undefined);

    // Mock successful login
    mockLogin.mockResolvedValueOnce({
      token: {
        access_token: 'test-token',
        token_type: 'bearer',
      },
      user: {
        id: 'user-1',
        username: 'newuser',
        created_at: new Date().toISOString(),
      },
    });

    render(<RegisterForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'newuser');
    await user.type(screen.getAllByLabelText(/password/i)[0], 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/chat');
    });
  });

  it('handles registration errors', async () => {
    const user = userEvent.setup();
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    mockRegister.mockRejectedValueOnce(new Error('Username already exists'));

    render(<RegisterForm />, { wrapper: createWrapper() });

    await user.type(screen.getByLabelText(/username/i), 'existinguser');
    await user.type(screen.getAllByLabelText(/password/i)[0], 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Registration failed:',
        expect.any(Error)
      );
    });

    expect(mockPush).not.toHaveBeenCalled();

    const authState = useAuthStore.getState();
    expect(authState.isAuthenticated).toBe(false);

    consoleErrorSpy.mockRestore();
  });

  it('requires all fields to be filled', () => {
    render(<RegisterForm />, { wrapper: createWrapper() });

    expect(screen.getByLabelText(/username/i)).toBeRequired();
    expect(screen.getAllByLabelText(/password/i)[0]).toBeRequired();
    expect(screen.getByLabelText(/confirm password/i)).toBeRequired();
  });
});
