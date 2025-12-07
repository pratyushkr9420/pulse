/**
 * Tests for SourcesList component.
 *
 * CORRECTED: All mock sources include required snippet field.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SourcesList } from '@/components/chat/SourcesList';
import type { Source } from '@/types/chat';

// CORRECTED: All sources include required snippet field
const mockSources: Source[] = [
  {
    title: 'Apple Stock Rises',
    ticker: 'AAPL',
    link: 'https://example.com/1',
    snippet: 'Apple stock rose 5% following strong quarterly earnings report...',
    relevance_score: 0.95,
  },
  {
    title: 'Microsoft Cloud Growth',
    ticker: 'MSFT',
    link: 'https://example.com/2',
    snippet: 'Microsoft Azure continued its strong growth trajectory in Q4...',
    relevance_score: 0.88,
  },
  {
    title: 'Amazon Expansion',
    ticker: 'AMZN',
    link: 'https://example.com/3',
    snippet: 'Amazon announced plans to expand its logistics network...',
    relevance_score: 0.82,
  },
];

describe('SourcesList', () => {
  it('renders all sources when under max', () => {
    render(<SourcesList sources={mockSources} maxDisplay={5} />);

    expect(screen.getByText('Apple Stock Rises')).toBeInTheDocument();
    expect(screen.getByText('Microsoft Cloud Growth')).toBeInTheDocument();
    expect(screen.getByText('Amazon Expansion')).toBeInTheDocument();
  });

  it('limits displayed sources to maxDisplay', () => {
    render(<SourcesList sources={mockSources} maxDisplay={2} />);

    expect(screen.getByText('Apple Stock Rises')).toBeInTheDocument();
    expect(screen.getByText('Microsoft Cloud Growth')).toBeInTheDocument();
    expect(screen.queryByText('Amazon Expansion')).not.toBeInTheDocument();
  });

  it('shows remaining count when sources exceed max', () => {
    render(<SourcesList sources={mockSources} maxDisplay={2} />);

    expect(screen.getByText('+1 more sources')).toBeInTheDocument();
  });

  it('returns null for empty sources', () => {
    const { container } = render(<SourcesList sources={[]} />);

    expect(container.firstChild).toBeNull();
  });

  it('displays ticker badges', () => {
    render(<SourcesList sources={mockSources.slice(0, 1)} />);

    expect(screen.getByText('AAPL')).toBeInTheDocument();
  });

  it('displays relevance scores', () => {
    render(<SourcesList sources={mockSources.slice(0, 1)} />);

    expect(screen.getByText('95% relevant')).toBeInTheDocument();
  });
});
