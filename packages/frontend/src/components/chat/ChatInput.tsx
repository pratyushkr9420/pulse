'use client';

/**
 * ChatInput component for message input.
 */

import { useState, FormEvent, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  isLoading = false,
  placeholder = 'Ask about stock news...',
}: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isLoading}
        className="flex-1 min-h-[44px] max-h-[120px] p-2 rounded-md border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-ring"
        rows={1}
      />
      <Button
        type="submit"
        disabled={!message.trim() || isLoading}
        size="icon"
      >
        <Send className="w-4 h-4" />
      </Button>
    </form>
  );
}
