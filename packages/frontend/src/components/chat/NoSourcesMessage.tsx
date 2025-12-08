/**
 * NoSourcesMessage component - Empty state for chat messages.
 *
 * Per .cursorrules specification (line 153).
 * Extracted from inline implementation in ChatContainer.
 */

'use client';

interface NoSourcesMessageProps {
  queryType?: 'general' | 'specific' | 'comparison';
}

export function NoSourcesMessage({ queryType = 'general' }: NoSourcesMessageProps) {
  const messages = {
    general: {
      title: 'Welcome to Pulse!',
      description: 'Ask me anything about AAPL, MSFT, AMZN, NFLX, NVDA, INTC, or IBM.',
    },
    specific: {
      title: 'No relevant articles found',
      description: "I couldn't find any articles matching your query. Try rephrasing or asking about a different topic.",
    },
    comparison: {
      title: 'Limited results',
      description: 'Some companies may not have articles available for comparison. Try different tickers or timeframes.',
    },
  };

  const message = messages[queryType];

  return (
    <div className="text-center text-muted-foreground py-8" data-testid="no-sources-message">
      <p className="text-lg font-medium">{message.title}</p>
      <p className="text-sm mt-2">{message.description}</p>
    </div>
  );
}
