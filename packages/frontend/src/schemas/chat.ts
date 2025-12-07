/**
 * Zod validation schemas for chat.
 *
 * CORRECTED: Now includes retriever_type and use_advanced_rag fields
 * to match backend ChatMessageCreate schema.
 */

import { z } from 'zod';

// Retriever type enum - matches backend
export const RetrieverTypeSchema = z.enum([
  'self_query',
  'base',
  'multi_query',
  'contextual_compression',
  'hybrid',
  'ensemble',
]);

// Source schema - CORRECTED: snippet is required
export const SourceSchema = z.object({
  title: z.string(),
  ticker: z.string(),
  link: z.string().url(),
  snippet: z.string(),  // Required field
  relevance_score: z.number().min(0).max(1),
});

// Chat message create schema - CORRECTED: includes all optional fields
export const ChatMessageCreateSchema = z.object({
  message: z.string().min(1).max(2000),
  ticker_filter: z.array(z.string()).nullable().optional(),
  retriever_type: RetrieverTypeSchema.optional().default('self_query'),
  use_advanced_rag: z.boolean().optional().default(false),
});

// Chat message response schema
export const ChatMessageSchema = z.object({
  id: z.string().uuid(),
  message: z.string(),
  response: z.string(),
  sources: z.array(SourceSchema),
  created_at: z.string(),
});

// Chat history response schema
export const ChatHistoryResponseSchema = z.object({
  items: z.array(ChatMessageSchema),
  total: z.number(),
});

// Type exports from schemas
export type ChatMessageCreateInput = z.infer<typeof ChatMessageCreateSchema>;
export type ChatMessageOutput = z.infer<typeof ChatMessageSchema>;
export type SourceOutput = z.infer<typeof SourceSchema>;
