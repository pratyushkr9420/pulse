/**
 * useChat hook - Chat operations using TanStack Query.
 *
 * Per .cursorrules specification (lines 170-173).
 * Encapsulates chat logic with chatStore integration.
 */

import { useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useChatStore } from '@/stores/chatStore';
import { apiClient } from '@/lib/api-client';
import type { ChatMessageInput, ChatHistoryResponse } from '@/types/chat';

export function useChat() {
  const queryClient = useQueryClient();
  const { setLoading, setPendingMessage, setError } = useChatStore();

  // Fetch chat history
  const { data: history, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => apiClient.getChatHistory(),
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (input: ChatMessageInput) => apiClient.sendMessage(input),
    onMutate: (input) => {
      // Optimistic update - show pending message
      setPendingMessage(input.message);
      setLoading(true);
    },
    onSuccess: (newMessage) => {
      // Clear pending state
      setPendingMessage(null);
      setLoading(false);
      setError(null);

      // Optimistically update cache with new message instead of refetching
      queryClient.setQueryData<ChatHistoryResponse>(['chatHistory'], (old) => {
        if (!old) {
          // If no existing data, create new structure
          return {
            items: [newMessage],
            total: 1,
          };
        }
        // Append new message to existing items
        return {
          items: [...old.items, newMessage],
          total: old.total + 1,
        };
      });
    },
    onError: (error: Error) => {
      setPendingMessage(null);
      setLoading(false);
      setError(error.message);
    },
  });

  const sendMessage = useCallback(
    (input: ChatMessageInput) => {
      sendMessageMutation.mutate(input);
    },
    [sendMessageMutation]
  );

  return {
    messages: history?.items ?? [],
    isLoading: isLoadingHistory || sendMessageMutation.isPending,
    error: sendMessageMutation.error?.message ?? null,
    sendMessage,
    isPending: sendMessageMutation.isPending,
  };
}
