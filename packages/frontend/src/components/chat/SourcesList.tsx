'use client';

/**
 * SourcesList component for displaying multiple sources.
 */

import { SourceCard } from './SourceCard';
import type { Source } from '@/types/chat';

interface SourcesListProps {
  sources: Source[];
  maxDisplay?: number;
}

export function SourcesList({ sources, maxDisplay = 5 }: SourcesListProps) {
  const displayedSources = sources.slice(0, maxDisplay);
  const remainingCount = sources.length - maxDisplay;

  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2">
      {displayedSources.map((source, idx) => (
        <SourceCard key={idx} source={source} />
      ))}

      {remainingCount > 0 && (
        <p className="text-xs text-muted-foreground text-center">
          +{remainingCount} more sources
        </p>
      )}
    </div>
  );
}
