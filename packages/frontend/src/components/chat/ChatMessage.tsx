'use client';

/**
 * ChatMessage component for displaying a single message.
 *
 * CORRECTED: Uses message/response fields (not content/role).
 * The ChatMessage type has:
 * - message: the user's original question
 * - response: the AI's answer
 */

import { formatDate } from '@/lib/utils';
import { SourceCard } from './SourceCard';
import type { ChatMessage as ChatMessageType } from '@/types/chat';

interface ChatMessageProps {
  message: ChatMessageType;
  isUser?: boolean;
}

export function ChatMessage({ message, isUser = false }: ChatMessageProps) {
  return (
    <div
      className={`flex flex-col gap-2 p-4 rounded-lg ${
        isUser ? 'bg-primary/10 ml-8' : 'bg-muted mr-8'
      }`}
    >
      <div className="flex justify-between items-start">
        <span className="font-medium text-sm">
          {isUser ? 'You' : 'Pulse'}
        </span>
        <span className="text-xs text-muted-foreground">
          {formatDate(message.created_at)}
        </span>
      </div>

      {/* CORRECTED: Display message for user, response for AI */}
      <p className="text-sm whitespace-pre-wrap">
        {isUser ? message.message : message.response}
      </p>

      {/* Show sources only for AI responses */}
      {!isUser && message.sources.length > 0 && (
        <div className="mt-2 pt-2 border-t">
          <p className="text-xs font-medium text-muted-foreground mb-2">
            Sources ({message.sources.length})
          </p>
          <div className="flex flex-col gap-2">
            {message.sources.map((source, idx) => (
              <SourceCard key={idx} source={source} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
