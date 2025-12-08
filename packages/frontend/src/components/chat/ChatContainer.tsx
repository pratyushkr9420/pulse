'use client';

/**
 * ChatContainer component - main chat interface.
 *
 * REFACTORED: Now uses centralized state management:
 * - Zustand for client state (RAG settings, UI state)
 * - TanStack Query for server state (via useChat hook)
 * - No direct useState for business logic
 */

import { useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { RAGSettings } from './RAGSettings';
import { TickerFilter } from './TickerFilter';
import { NoSourcesMessage } from './NoSourcesMessage';
import { useChat } from '@/hooks/useChat';
import { useChatStore } from '@/stores/chatStore';
import { useRagSettingsStore } from '@/stores/ragSettingsStore';

export function ChatContainer() {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Server state via centralized hook
  const { messages, isLoading, sendMessage, isPending } = useChat();

  // Client state from Zustand stores
  const pendingMessage = useChatStore((state) => state.pendingMessage);
  const retrieverType = useRagSettingsStore((state) => state.retrieverType);
  const setRetrieverType = useRagSettingsStore((state) => state.setRetrieverType);
  const useAdvancedRag = useRagSettingsStore((state) => state.useAdvancedRag);
  const setUseAdvancedRag = useRagSettingsStore((state) => state.setUseAdvancedRag);
  const tickerFilter = useRagSettingsStore((state) => state.tickerFilter);
  const setTickerFilter = useRagSettingsStore((state) => state.setTickerFilter);
  const showSettings = useRagSettingsStore((state) => state.showSettings);
  const setShowSettings = useRagSettingsStore((state) => state.setShowSettings);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, pendingMessage]);

  const handleSend = (message: string) => {
    sendMessage({
      message,
      tickerFilter: tickerFilter.length > 0 ? tickerFilter : undefined,
      retrieverType,
      useAdvancedRag,
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header with settings toggle */}
      <div className="flex justify-between items-center p-4 border-b">
        <h2 className="font-semibold">Chat</h2>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          {showSettings ? 'Hide Settings' : 'Show Settings'}
        </button>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div className="p-4 border-b bg-muted/30">
          <div className="flex flex-col gap-4 max-w-md">
            <RAGSettings
              retrieverType={retrieverType}
              onRetrieverTypeChange={setRetrieverType}
              useAdvancedRag={useAdvancedRag}
              onAdvancedRagChange={setUseAdvancedRag}
            />
            <TickerFilter
              selected={tickerFilter}
              onChange={setTickerFilter}
            />
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : messages.length === 0 && !pendingMessage ? (
          <NoSourcesMessage queryType="general" />
        ) : (
          <>
            {/* Render message pairs - each ChatMessage contains both user Q and AI A */}
            {messages.map((msg) => (
              <div key={msg.id} className="space-y-2">
                {/* User's message */}
                <ChatMessage message={msg} isUser={true} />
                {/* AI's response */}
                <ChatMessage message={msg} isUser={false} />
              </div>
            ))}

            {/* Pending user message (optimistic) */}
            {pendingMessage && (
              <div className="space-y-2">
                <div className="p-4 rounded-lg bg-primary/10 ml-8">
                  <p className="text-sm">{pendingMessage}</p>
                </div>
                <div className="p-4 rounded-lg bg-muted mr-8">
                  <p className="text-sm text-muted-foreground animate-pulse">
                    Thinking...
                  </p>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t">
        <ChatInput
          onSend={handleSend}
          isLoading={isPending}
        />
      </div>
    </div>
  );
}
