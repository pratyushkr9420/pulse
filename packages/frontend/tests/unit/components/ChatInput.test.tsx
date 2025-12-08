/**
 * Tests for ChatInput component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatInput } from '@/components/chat/ChatInput';

describe('ChatInput', () => {
  const defaultProps = {
    onSend: vi.fn(),
    isLoading: false,
  };

  it('renders input field', () => {
    render(<ChatInput {...defaultProps} />);

    expect(screen.getByPlaceholderText(/ask about/i)).toBeInTheDocument();
  });

  it('renders send button', () => {
    render(<ChatInput {...defaultProps} />);

    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onSend when form is submitted', async () => {
    const user = userEvent.setup();
    const mockSend = vi.fn();
    render(<ChatInput {...defaultProps} onSend={mockSend} />);

    const input = screen.getByPlaceholderText(/ask about/i);
    await user.type(input, 'What is the latest AAPL news?');
    await user.click(screen.getByRole('button'));

    expect(mockSend).toHaveBeenCalledWith('What is the latest AAPL news?');
  });

  it('clears input after submission', async () => {
    const user = userEvent.setup();
    render(<ChatInput {...defaultProps} />);

    const input = screen.getByPlaceholderText(/ask about/i);
    await user.type(input, 'Test message');
    await user.click(screen.getByRole('button'));

    expect(input).toHaveValue('');
  });

  it('disables input when loading', () => {
    render(<ChatInput {...defaultProps} isLoading={true} />);

    expect(screen.getByPlaceholderText(/ask about/i)).toBeDisabled();
  });

  it('disables button when loading', () => {
    render(<ChatInput {...defaultProps} isLoading={true} />);

    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('does not submit empty messages', async () => {
    const user = userEvent.setup();
    const mockSend = vi.fn();
    render(<ChatInput {...defaultProps} onSend={mockSend} />);

    await user.click(screen.getByRole('button'));

    expect(mockSend).not.toHaveBeenCalled();
  });
});
