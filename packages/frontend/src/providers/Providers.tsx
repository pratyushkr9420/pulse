'use client';

/**
 * Providers component - Global provider setup.
 *
 * Wraps the app with necessary providers:
 * - QueryClientProvider for TanStack Query (server state)
 * - Zustand stores are used directly via hooks (no provider needed)
 */

import { ReactNode, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

export function Providers({ children }: { children: ReactNode }) {
  // Create QueryClient instance per app instance
  // Using useState ensures client is only created once per render
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
