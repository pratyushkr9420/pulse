/**
 * Tests for SourceCard component.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SourceCard } from '@/components/chat/SourceCard';
import type { Source } from '@/types/chat';

const mockSource: Source = {
  title: 'Apple Announces New Products',
  ticker: 'AAPL',
  link: 'https://example.com/apple-news',
  snippet: 'Apple Inc. unveiled its latest lineup of products at the annual event...',
  relevance_score: 0.95,
};

describe('SourceCard', () => {
  it('renders source title', () => {
    render(<SourceCard source={mockSource} />);

    expect(screen.getByText('Apple Announces New Products')).toBeInTheDocument();
  });

  it('renders ticker badge', () => {
    render(<SourceCard source={mockSource} />);

    expect(screen.getByText('AAPL')).toBeInTheDocument();
  });

  it('renders snippet text', () => {
    render(<SourceCard source={mockSource} />);

    expect(screen.getByText(/Apple Inc. unveiled its latest lineup/)).toBeInTheDocument();
  });

  it('renders relevance score', () => {
    render(<SourceCard source={mockSource} />);

    // Score is rendered as "95% relevant" but split across text nodes
    // Use regex to find the percentage text
    expect(screen.getByText(/95/)).toBeInTheDocument();
    expect(screen.getByText(/% relevant/)).toBeInTheDocument();
  });

  it('has link with correct href', () => {
    render(<SourceCard source={mockSource} />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', 'https://example.com/apple-news');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('displays relevance score as percentage', () => {
    // Render with 0.75 relevance score
    const sourceWithDifferentScore = { ...mockSource, relevance_score: 0.75 };
    render(<SourceCard source={sourceWithDifferentScore} />);

    // Should show 75% relevant (split across text nodes)
    expect(screen.getByText(/75/)).toBeInTheDocument();
    expect(screen.getByText(/% relevant/)).toBeInTheDocument();
  });
});
