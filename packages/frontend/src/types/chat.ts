/**
 * Chat-related TypeScript types.
 *
 * CORRECTED: These types now match the backend Pydantic schemas exactly.
 * - ChatMessage uses message/response (not content/role)
 * - Source includes required snippet field
 * - RetrieverType matches backend enum
 */

// Retriever types available - matches backend RetrieverTypeEnum
export type RetrieverType =
  | 'self_query'
  | 'base'
  | 'multi_query'
  | 'contextual_compression'
  | 'hybrid'
  | 'ensemble';

// Source information for cited articles - matches backend SourceInfo
export interface Source {
  title: string;
  ticker: string;
  link: string;
  snippet: string;  // CORRECTED: This field is required, was missing in some mocks
  relevance_score: number;
}

// Chat message from API - matches backend ChatMessageResponse
export interface ChatMessage {
  id: string;
  message: string;      // User's message (NOT 'content')
  response: string;     // AI's response (NOT 'role')
  sources: Source[];
  created_at: string;
}

// Request to create a chat message - matches backend ChatMessageCreate
// Note: Uses snake_case for API compatibility
export interface ChatMessageCreate {
  message: string;
  ticker_filter?: string[] | null;
  retriever_type?: RetrieverType;
  use_advanced_rag?: boolean;
}

// Internal type for UI state (camelCase convention)
export interface ChatMessageInput {
  message: string;
  tickerFilter?: string[];
  retrieverType?: RetrieverType;
  useAdvancedRag?: boolean;
}

// Chat history response - matches backend ChatHistoryResponse
export interface ChatHistoryResponse {
  items: ChatMessage[];
  total: number;
}

// Helper to convert UI input to API format
export function toApiFormat(input: ChatMessageInput): ChatMessageCreate {
  return {
    message: input.message,
    ticker_filter: input.tickerFilter ?? null,
    retriever_type: input.retrieverType ?? 'self_query',
    use_advanced_rag: input.useAdvancedRag ?? false,
  };
}
