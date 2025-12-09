/**
 * API client for backend communication.
 */

import type {
  ChatMessage,
  ChatMessageInput,
  ChatHistoryResponse,
} from '@/types/chat';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from '@/types/auth';
import { toApiFormat } from '@/types/chat';
import { getToken } from '@/lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Parse error response from FastAPI.
 * Tries to parse JSON first (FastAPI format), then falls back to text, then statusText.
 */
async function parseErrorResponse(response: Response): Promise<string> {
  try {
    const data = await response.json();
    if (data.detail) {
      // Handle Pydantic validation errors (array format)
      if (Array.isArray(data.detail)) {
        return data.detail[0]?.msg || response.statusText;
      }
      // Handle standard FastAPI errors (string format)
      return data.detail;
    }
    return response.statusText;
  } catch {
    // JSON parsing failed, try plain text
    try {
      const text = await response.text();
      return text || response.statusText;
    } catch {
      // Both JSON and text parsing failed
      return response.statusText;
    }
  }
}

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
    const error = await parseErrorResponse(response);
    throw new Error(error);
  }

  return response.json();
}

/**
 * API client object.
 */
export const apiClient = {
  /**
   * Login user and return token and user info.
   */
  async login(credentials: LoginRequest): Promise<{ token: TokenResponse; user: User }> {
    // Auth endpoint uses form-urlencoded, not JSON
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await parseErrorResponse(response);
      throw new Error(error);
    }

    const token = await response.json() as TokenResponse;

    // Fetch user info with the new token
    const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token.access_token}`,
      },
    });

    if (!userResponse.ok) {
      const error = await parseErrorResponse(userResponse);
      throw new Error(error);
    }

    const user = await userResponse.json() as User;

    return { token, user };
  },

  /**
   * Register a new user.
   */
  async register(data: RegisterRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await parseErrorResponse(response);
      throw new Error(error);
    }
  },

  /**
   * Get current user info.
   */
  async getMe(): Promise<User> {
    return fetchWithAuth<User>('/api/v1/auth/me');
  },

  /**
   * Get chat history.
   */
  async getChatHistory(): Promise<ChatHistoryResponse> {
    return fetchWithAuth<ChatHistoryResponse>('/api/v1/chat/history');
  },

  /**
   * Send a chat message.
   */
  async sendMessage(input: ChatMessageInput): Promise<ChatMessage> {
    const apiInput = toApiFormat(input);
    return fetchWithAuth<ChatMessage>('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(apiInput),
    });
  },
};
