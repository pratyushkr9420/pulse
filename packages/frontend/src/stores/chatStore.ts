/**
 * Zustand store for chat state.
 *
 * Per .cursorrules specification (lines 176-177).
 * Manages chat history and UI state.
 */

import { create } from 'zustand';
import type { ChatMessage, ChatState } from '@/types/chat';

interface ChatActions {
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPendingMessage: (message: string | null) => void;
  clearMessages: () => void;
}

type ChatStore = ChatState & ChatActions;

export const useChatStore = create<ChatStore>((set) => ({
  // State
  messages: [],
  isLoading: false,
  error: null,
  pendingMessage: null,

  // Actions
  setMessages: (messages) =>
    set({ messages }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
      pendingMessage: null,
    })),

  setLoading: (isLoading) =>
    set({ isLoading }),

  setError: (error) =>
    set({ error }),

  setPendingMessage: (pendingMessage) =>
    set({ pendingMessage }),

  clearMessages: () =>
    set({ messages: [], error: null, pendingMessage: null }),
}));
