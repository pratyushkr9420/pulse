'use client';

/**
 * SourceCard component for displaying a cited source.
 * Displays title, ticker, snippet, and relevance score.
 */

import { ExternalLink } from 'lucide-react';
import { truncate } from '@/lib/utils';
import type { Source } from '@/types/chat';

interface SourceCardProps {
  source: Source;
}

export function SourceCard({ source }: SourceCardProps) {
  const relevancePercent = Math.round(source.relevance_score * 100);

  return (
    <a
      href={source.link}
      target="_blank"
      rel="noopener noreferrer"
      className="flex flex-col gap-1 p-2 rounded border bg-card hover:bg-accent/50 transition-colors"
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium">{source.title}</span>
        <ExternalLink className="w-3 h-3 text-muted-foreground" />
      </div>

      {/* Snippet - required field */}
      <p className="text-xs text-muted-foreground">
        {truncate(source.snippet, 150)}
      </p>

      <div className="flex items-center justify-between text-xs">
        <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary font-medium">
          {source.ticker}
        </span>
        <span className="text-muted-foreground">
          {relevancePercent}% relevant
        </span>
      </div>
    </a>
  );
}
