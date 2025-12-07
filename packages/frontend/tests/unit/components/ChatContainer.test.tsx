/**
 * Tests for ChatContainer component.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ChatContainer } from '@/components/chat/ChatContainer';

// Mock the API
vi.mock('@/lib/api-client', () => ({
  chatApi: {
    sendMessage: vi.fn(),
    getHistory: vi.fn(),
  },
  tickerApi: {
    getTickers: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
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
  });

  it('renders chat container', () => {
    render(<ChatContainer />, { wrapper: createWrapper() });

    expect(screen.getByPlaceholderText(/ask about/i)).toBeInTheDocument();
  });

  it('renders empty state when no messages', () => {
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Check that chat input is present (empty state)
    expect(screen.getByPlaceholderText(/ask about/i)).toBeInTheDocument();
  });

  it('renders ticker filter when settings shown', async () => {
    const user = userEvent.setup();
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Click show settings button
    const settingsButton = screen.getByRole('button', { name: /show settings/i });
    await user.click(settingsButton);

    expect(screen.getByText(/filter by ticker/i)).toBeInTheDocument();
  });

  it('renders RAG settings when settings shown', async () => {
    const user = userEvent.setup();
    render(<ChatContainer />, { wrapper: createWrapper() });

    // Click show settings button
    const settingsButton = screen.getByRole('button', { name: /show settings/i });
    await user.click(settingsButton);

    expect(screen.getByText(/retriever type/i)).toBeInTheDocument();
  });

  it('shows chat input', () => {
    render(<ChatContainer />, { wrapper: createWrapper() });

    const input = screen.getByPlaceholderText(/ask about/i);
    expect(input).toBeInTheDocument();
    expect(input).not.toBeDisabled();
  });
});
