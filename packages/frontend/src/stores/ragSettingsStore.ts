/**
 * Zustand store for RAG settings state.
 *
 * Manages retriever type, advanced RAG toggle, and ticker filters.
 * Per architectural requirement: client state managed by Zustand.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { RagSettingsState, RetrieverType } from '@/types/chat';

interface RagSettingsActions {
  setRetrieverType: (type: RetrieverType) => void;
  setUseAdvancedRag: (use: boolean) => void;
  setTickerFilter: (tickers: string[]) => void;
  toggleTicker: (ticker: string) => void;
  selectAllTickers: () => void;
  clearAllTickers: () => void;
  setShowSettings: (show: boolean) => void;
  resetSettings: () => void;
}

type RagSettingsStore = RagSettingsState & RagSettingsActions;

const AVAILABLE_TICKERS = ['AAPL', 'MSFT', 'AMZN', 'NFLX', 'NVDA', 'INTC', 'IBM'];

const initialState: RagSettingsState = {
  retrieverType: 'self_query',
  useAdvancedRag: false,
  tickerFilter: [],
  showSettings: false,
};

export const useRagSettingsStore = create<RagSettingsStore>()(
  persist(
    (set) => ({
      ...initialState,

      setRetrieverType: (retrieverType) => set({ retrieverType }),

      setUseAdvancedRag: (useAdvancedRag) => set({ useAdvancedRag }),

      setTickerFilter: (tickerFilter) => set({ tickerFilter }),

      toggleTicker: (ticker) =>
        set((state) => ({
          tickerFilter: state.tickerFilter.includes(ticker)
            ? state.tickerFilter.filter((t) => t !== ticker)
            : [...state.tickerFilter, ticker],
        })),

      selectAllTickers: () =>
        set({ tickerFilter: [...AVAILABLE_TICKERS] }),

      clearAllTickers: () =>
        set({ tickerFilter: [] }),

      setShowSettings: (showSettings) => set({ showSettings }),

      resetSettings: () => set(initialState),
    }),
    {
      name: 'pulse-rag-settings',
      partialize: (state) => ({
        retrieverType: state.retrieverType,
        useAdvancedRag: state.useAdvancedRag,
        tickerFilter: state.tickerFilter,
      }),
    }
  )
);

// Export available tickers constant
export const AVAILABLE_TICKERS_LIST = AVAILABLE_TICKERS;
