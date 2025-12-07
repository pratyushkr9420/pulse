'use client';

/**
 * GroupedSourcesList component - groups sources by ticker.
 */

import { SourceCard } from './SourceCard';
import type { Source } from '@/types/chat';

interface GroupedSourcesListProps {
  sources: Source[];
}

export function GroupedSourcesList({ sources }: GroupedSourcesListProps) {
  // Group sources by ticker
  const grouped = sources.reduce<Record<string, Source[]>>((acc, source) => {
    const ticker = source.ticker;
    if (!acc[ticker]) {
      acc[ticker] = [];
    }
    acc[ticker].push(source);
    return acc;
  }, {});

  const tickers = Object.keys(grouped).sort();

  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-4">
      {tickers.map((ticker) => (
        <div key={ticker}>
          <h4 className="text-sm font-medium mb-2">{ticker}</h4>
          <div className="flex flex-col gap-2">
            {grouped[ticker].map((source, idx) => (
              <SourceCard key={idx} source={source} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
