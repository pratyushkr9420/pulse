/**
 * API client for backend communication.
 */

import type {
  ChatMessage,
  ChatMessageInput,
  ChatHistoryResponse,
} from '@/types/chat';
import { toApiFormat } from '@/types/chat';
import { getToken } from '@/lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Helper to make authenticated API requests.
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || response.statusText);
  }

  return response.json();
}

/**
 * API client object.
 */
export const apiClient = {
  /**
   * Get chat history.
   */
  async getChatHistory(): Promise<ChatHistoryResponse> {
    return fetchWithAuth<ChatHistoryResponse>('/api/chat/history');
  },

  /**
   * Send a chat message.
   */
  async sendMessage(input: ChatMessageInput): Promise<ChatMessage> {
    const apiInput = toApiFormat(input);
    return fetchWithAuth<ChatMessage>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(apiInput),
    });
  },
};
