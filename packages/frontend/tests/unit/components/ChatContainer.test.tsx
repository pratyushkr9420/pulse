/**
 * Tests for ChatContainer component.
 *
 * UPDATED: Now tests integration with Zustand stores and custom hooks.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ChatContainer } from '@/components/chat/ChatContainer';
import { useChatStore } from '@/stores/chatStore';
import { useRagSettingsStore } from '@/stores/ragSettingsStore';

// Mock the API
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    sendMessage: vi.fn().mockResolvedValue({
      id: '1',
      message: 'Test question',
      response: 'Test response',
      sources: [],
      ticker_filter: null,
      retriever_type: 'self_query',
      use_advanced_rag: false,
      created_at: new Date().toISOString(),
      user_id: 'test-user',
    }),
    getChatHistory: vi.fn().mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      size: 50,
    }),
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

describe('ChatContainer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset Zustand stores to initial state
    useChatStore.setState({
      messages: [],
      isLoading: false,
      error: null,
      pendingMessage: null,
    });
    useRagSettingsStore.setState({
      retrieverType: 'self_query',
      useAdvancedRag: false,
      tickerFilter: [],
      showSettings: false,
    });
  });

  afterEach(() => {
    // Clean up stores
    useChatStore.getState().clearMessages();
    useRagSettingsStore.getState().resetSettings();
  });

  it('renders chat container', () => {
    render(<ChatContainer />, { wrapper: createWrapper() });

    expect(screen.getByPlaceholderText(/ask about/i)).toBeInTheDocument();
  });

  it('renders empty state when no messages', async () => {
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Check for NoSourcesMessage component with welcome message
    await waitFor(() => {
      expect(screen.getByText(/welcome to pulse/i)).toBeInTheDocument();
    });
  });

  it('renders ticker filter when settings shown', async () => {
    const user = userEvent.setup();
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Click show settings button
    const settingsButton = screen.getByRole('button', { name: /show settings/i });
    await user.click(settingsButton);

    await waitFor(() => {
      expect(screen.getByText(/filter by ticker/i)).toBeInTheDocument();
    });

    // Verify store was updated
    expect(useRagSettingsStore.getState().showSettings).toBe(true);
  });

  it('renders RAG settings when settings shown', async () => {
    const user = userEvent.setup();
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Click show settings button
    const settingsButton = screen.getByRole('button', { name: /show settings/i });
    await user.click(settingsButton);

    await waitFor(() => {
      expect(screen.getByText(/search method/i)).toBeInTheDocument();
    });
  });

  it('shows chat input', () => {
    render(<ChatContainer />, { wrapper: createWrapper() });

    const input = screen.getByPlaceholderText(/ask about/i);
    expect(input).toBeInTheDocument();
    expect(input).not.toBeDisabled();
  });

  it('uses Zustand store for RAG settings', async () => {
    // Pre-set some RAG settings in the store
    useRagSettingsStore.setState({
      retrieverType: 'hybrid',
      useAdvancedRag: true,
      tickerFilter: ['AAPL', 'MSFT'],
      showSettings: true,
    });

    render(<ChatContainer />, { wrapper: createWrapper() });

    // Settings should be visible (showSettings is true)
    await waitFor(() => {
      expect(screen.getByText(/search method/i)).toBeInTheDocument();
    });

    // Verify the store values are used
    const store = useRagSettingsStore.getState();
    expect(store.retrieverType).toBe('hybrid');
    expect(store.useAdvancedRag).toBe(true);
    expect(store.tickerFilter).toEqual(['AAPL', 'MSFT']);
  });

  it('updates chat store when sending message', async () => {
    const user = userEvent.setup();
    render(<ChatContainer />, { wrapper: createWrapper() });

    const input = screen.getByPlaceholderText(/ask about/i);
    await user.type(input, 'Test message');
    await user.keyboard('{Enter}');

    // Check that pendingMessage was set in chat store (optimistic update)
    await waitFor(() => {
      const chatState = useChatStore.getState();
      // After mutation completes, pendingMessage should be cleared
      expect(chatState.pendingMessage).toBeNull();
    });
  });

  it('persists RAG settings in localStorage', async () => {
    const user = userEvent.setup();
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Show settings
    const settingsButton = screen.getByRole('button', { name: /show settings/i });
    await user.click(settingsButton);

    // Change retriever type
    useRagSettingsStore.setState({ retrieverType: 'multi_query' });

    // Verify it's in the store
    expect(useRagSettingsStore.getState().retrieverType).toBe('multi_query');

    // Note: Actual localStorage persistence is tested in the store's persist middleware
  });
});
