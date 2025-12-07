/**
 * Tests for GroupedSourcesList component.
 *
 * CORRECTED: All mock sources include required snippet field.
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GroupedSourcesList } from '@/components/chat/GroupedSourcesList';
import type { Source } from '@/types/chat';

// CORRECTED: All sources include required snippet field
const mockSources: Source[] = [
  {
    title: 'Apple Q4 Results',
    ticker: 'AAPL',
    link: 'https://example.com/1',
    snippet: 'Apple reported record Q4 revenue driven by iPhone sales...',
    relevance_score: 0.95,
  },
  {
    title: 'Apple New Products',
    ticker: 'AAPL',
    link: 'https://example.com/2',
    snippet: 'Apple unveiled new MacBook Pro models with M3 chips...',
    relevance_score: 0.90,
  },
  {
    title: 'Microsoft AI Push',
    ticker: 'MSFT',
    link: 'https://example.com/3',
    snippet: 'Microsoft continues investment in AI across product lines...',
    relevance_score: 0.85,
  },
];

describe('GroupedSourcesList', () => {
  it('groups sources by ticker', () => {
    render(<GroupedSourcesList sources={mockSources} />);

    // Should have section headers for each ticker
    const headings = screen.getAllByRole('heading', { level: 4 });
    expect(headings.find((h) => h.textContent === 'AAPL')).toBeInTheDocument();
    expect(headings.find((h) => h.textContent === 'MSFT')).toBeInTheDocument();
  });

  it('displays all sources under correct ticker', () => {
    render(<GroupedSourcesList sources={mockSources} />);

    expect(screen.getByText('Apple Q4 Results')).toBeInTheDocument();
    expect(screen.getByText('Apple New Products')).toBeInTheDocument();
    expect(screen.getByText('Microsoft AI Push')).toBeInTheDocument();
  });

  it('returns null for empty sources', () => {
    const { container } = render(<GroupedSourcesList sources={[]} />);

    expect(container.firstChild).toBeNull();
  });

  it('sorts tickers alphabetically', () => {
    render(<GroupedSourcesList sources={mockSources} />);

    const headings = screen.getAllByRole('heading', { level: 4 });
    expect(headings[0]).toHaveTextContent('AAPL');
    expect(headings[1]).toHaveTextContent('MSFT');
  });
});
