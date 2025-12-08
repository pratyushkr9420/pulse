/**
 * SourcesLoading component - Loading skeleton for chat responses.
 *
 * Per .cursorrules specification (line 154).
 * Extracted from inline implementation in ChatContainer.
 */

'use client';

export function SourcesLoading() {
  return (
    <div className="flex flex-col gap-3" data-testid="sources-loading">
      {/* Skeleton for AI response */}
      <div className="p-4 rounded-lg bg-muted mr-8">
        <div className="space-y-2">
          <div className="h-4 bg-muted-foreground/20 rounded animate-pulse w-3/4"></div>
          <div className="h-4 bg-muted-foreground/20 rounded animate-pulse w-1/2"></div>
        </div>
      </div>

      {/* Skeleton for sources */}
      <div className="flex flex-col gap-2 mr-8">
        {[1, 2, 3].map((i) => (
          <div key={i} className="p-3 rounded-lg border bg-card">
            <div className="space-y-2">
              <div className="h-3 bg-muted-foreground/20 rounded animate-pulse w-full"></div>
              <div className="h-3 bg-muted-foreground/20 rounded animate-pulse w-5/6"></div>
              <div className="h-3 bg-muted-foreground/20 rounded animate-pulse w-1/3"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
