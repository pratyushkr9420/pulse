/**
 * Tests for TickerFilter component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TickerFilter } from '@/components/chat/TickerFilter';

const SUPPORTED_TICKERS = ['AAPL', 'MSFT', 'AMZN', 'NFLX', 'NVDA', 'INTC', 'IBM'];

describe('TickerFilter', () => {
  const defaultProps = {
    selected: [] as string[],
    onChange: vi.fn(),
  };

  it('renders filter component', () => {
    render(<TickerFilter {...defaultProps} />);

    expect(screen.getByText(/filter by ticker/i)).toBeInTheDocument();
  });

  it('displays all available tickers', () => {
    render(<TickerFilter {...defaultProps} />);

    // All tickers should be visible as badges
    for (const ticker of SUPPORTED_TICKERS) {
      expect(screen.getByText(ticker)).toBeInTheDocument();
    }
  });

  it('calls onChange when ticker is selected', async () => {
    const user = userEvent.setup();
    const mockChange = vi.fn();
    render(<TickerFilter {...defaultProps} onChange={mockChange} />);

    // Click on AAPL badge to select it
    await user.click(screen.getByText('AAPL'));

    expect(mockChange).toHaveBeenCalledWith(['AAPL']);
  });

  it('shows selected tickers as badges', () => {
    render(<TickerFilter {...defaultProps} selected={['AAPL', 'MSFT']} />);

    // Selected tickers should be shown with default variant (filled)
    const badges = screen.getAllByText(/AAPL|MSFT/);
    expect(badges.length).toBeGreaterThanOrEqual(2);
  });

  it('allows removing selected tickers', async () => {
    const user = userEvent.setup();
    const mockChange = vi.fn();
    render(
      <TickerFilter
        {...defaultProps}
        selected={['AAPL', 'MSFT']}
        onChange={mockChange}
      />
    );

    // Click on AAPL badge to deselect it
    const aaplBadge = screen.getByText('AAPL');
    await user.click(aaplBadge);

    // Should be called with AAPL removed
    expect(mockChange).toHaveBeenCalledWith(['MSFT']);
  });

  it('allows clearing all filters', async () => {
    const user = userEvent.setup();
    const mockChange = vi.fn();
    render(
      <TickerFilter
        {...defaultProps}
        selected={['AAPL', 'MSFT']}
        onChange={mockChange}
      />
    );

    const clearButton = screen.getByText(/clear all/i);
    await user.click(clearButton);

    expect(mockChange).toHaveBeenCalledWith([]);
  });
});
