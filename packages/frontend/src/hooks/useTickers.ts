/**
 * useTickers hook - Ticker filter state management.
 *
 * Per .cursorrules specification (lines 170-173).
 * Now wraps ragSettingsStore for centralized state management.
 */

import { useRagSettingsStore, AVAILABLE_TICKERS_LIST } from '@/stores/ragSettingsStore';

export function useTickers() {
  const selectedTickers = useRagSettingsStore((state) => state.tickerFilter);
  const toggleTicker = useRagSettingsStore((state) => state.toggleTicker);
  const selectAll = useRagSettingsStore((state) => state.selectAllTickers);
  const clearAll = useRagSettingsStore((state) => state.clearAllTickers);
  const setTickers = useRagSettingsStore((state) => state.setTickerFilter);

  return {
    selectedTickers,
    toggleTicker,
    selectAll,
    clearAll,
    setTickers,
    availableTickers: AVAILABLE_TICKERS_LIST,
  };
}
