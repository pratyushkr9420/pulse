'use client';

/**
 * ChatContainer component - main chat interface.
 *
 * CORRECTED: Properly handles user vs AI message display.
 * User messages only need the 'message' field displayed.
 * AI messages show 'response' and 'sources'.
 */

import { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { RAGSettings } from './RAGSettings';
import { TickerFilter } from './TickerFilter';
import { apiClient } from '@/lib/api-client';
import type { ChatMessage as ChatMessageType, RetrieverType, ChatMessageInput } from '@/types/chat';

export function ChatContainer() {
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Local state for pending user messages (optimistic UI)
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  // RAG settings state
  const [retrieverType, setRetrieverType] = useState<RetrieverType>('self_query');
  const [useAdvancedRag, setUseAdvancedRag] = useState(false);
  const [tickerFilter, setTickerFilter] = useState<string[]>([]);
  const [showSettings, setShowSettings] = useState(false);

  // Fetch chat history
  const { data: history, isLoading } = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => apiClient.getChatHistory(),
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (input: ChatMessageInput) => apiClient.sendMessage(input),
    onMutate: (input) => {
      // Optimistic update - show user message immediately
      setPendingMessage(input.message);
    },
    onSuccess: () => {
      // Clear pending and refetch history
      setPendingMessage(null);
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
    },
    onError: () => {
      setPendingMessage(null);
    },
  });

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history?.items, pendingMessage]);

  const handleSend = (message: string) => {
    sendMessageMutation.mutate({
      message,
      tickerFilter: tickerFilter.length > 0 ? tickerFilter : undefined,
      retrieverType,
      useAdvancedRag,
    });
  };

  const messages = history?.items ?? [];

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
          <div className="text-center text-muted-foreground py-8">
            <p className="text-lg font-medium">Welcome to Pulse!</p>
            <p className="text-sm mt-2">
              Ask me anything about AAPL, MSFT, AMZN, NFLX, NVDA, INTC, or IBM.
            </p>
          </div>
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
          isLoading={sendMessageMutation.isPending}
        />
      </div>
    </div>
  );
}
