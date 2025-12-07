/**
 * Tests for ChatMessage component.
 * 
 * CORRECTED: Mocks use message/response fields (not content/role).
 * All source mocks include required snippet field.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ChatMessage } from '@/components/chat/ChatMessage';
import type { ChatMessage as ChatMessageType } from '@/types/chat';

// CORRECTED: Mock uses correct ChatMessage type with message/response
const mockMessage: ChatMessageType = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  message: 'What is the latest AAPL news?',
  response: 'Apple announced new products today.',
  sources: [
    {
      title: 'Apple News',
      ticker: 'AAPL',
      link: 'https://example.com/apple',
      snippet: 'Apple Inc. announced several new products at their annual event...',  // CORRECTED: Required field
      relevance_score: 0.92,
    },
  ],
  created_at: '2024-01-15T10:30:00Z',
};

describe('ChatMessage', () => {
  it('renders user message correctly', () => {
    render(<ChatMessage message={mockMessage} isUser={true} />);
    
    // User messages display the 'message' field
    expect(screen.getByText('What is the latest AAPL news?')).toBeInTheDocument();
    expect(screen.getByText('You')).toBeInTheDocument();
  });

  it('renders AI response correctly', () => {
    render(<ChatMessage message={mockMessage} isUser={false} />);
    
    // AI messages display the 'response' field
    expect(screen.getByText('Apple announced new products today.')).toBeInTheDocument();
    expect(screen.getByText('Pulse')).toBeInTheDocument();
  });

  it('displays sources for AI messages', () => {
    render(<ChatMessage message={mockMessage} isUser={false} />);
    
    expect(screen.getByText('Sources (1)')).toBeInTheDocument();
    expect(screen.getByText('Apple News')).toBeInTheDocument();
  });

  it('does not display sources for user messages', () => {
    render(<ChatMessage message={mockMessage} isUser={true} />);
    
    expect(screen.queryByText('Sources')).not.toBeInTheDocument();
  });

  it('displays timestamp', () => {
    render(<ChatMessage message={mockMessage} isUser={false} />);
    
    // The formatDate function should render the date
    expect(screen.getByText(/Jan/)).toBeInTheDocument();
  });
});
