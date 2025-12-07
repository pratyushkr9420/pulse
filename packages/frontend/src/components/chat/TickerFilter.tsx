'use client';

/**
 * TickerFilter component for filtering by stock ticker.
 */

import { Badge } from '@/components/ui/badge';

const TICKERS = ['AAPL', 'MSFT', 'AMZN', 'NFLX', 'NVDA', 'INTC', 'IBM'];

interface TickerFilterProps {
  selected: string[];
  onChange: (tickers: string[]) => void;
}

export function TickerFilter({ selected, onChange }: TickerFilterProps) {
  const toggleTicker = (ticker: string) => {
    if (selected.includes(ticker)) {
      onChange(selected.filter((t) => t !== ticker));
    } else {
      onChange([...selected, ticker]);
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <span className="text-sm font-medium">Filter by Ticker</span>
      <div className="flex flex-wrap gap-2">
        {TICKERS.map((ticker) => (
          <Badge
            key={ticker}
            variant={selected.includes(ticker) ? 'default' : 'outline'}
            className="cursor-pointer"
            onClick={() => toggleTicker(ticker)}
          >
            {ticker}
          </Badge>
        ))}
      </div>
      {selected.length > 0 && (
        <button
          onClick={() => onChange([])}
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          Clear all
        </button>
      )}
    </div>
  );
}
