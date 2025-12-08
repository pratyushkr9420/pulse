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
import type { ChatMessageInput } from '@/types/chat';

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
      // Optimistic update
      setPendingMessage(input.message);
      setLoading(true);
    },
    onSuccess: () => {
      // Clear pending and refetch
      setPendingMessage(null);
      setLoading(false);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] });
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
