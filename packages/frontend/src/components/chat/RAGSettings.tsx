'use client';

/**
 * RAGSettings component for configuring RAG options.
 *
 * CORRECTED: Uses proper data-testid for reliable test selection.
 */

import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { RetrieverType } from '@/types/chat';

interface RAGSettingsProps {
  retrieverType: RetrieverType;
  onRetrieverTypeChange: (type: RetrieverType) => void;
  useAdvancedRag: boolean;
  onAdvancedRagChange: (enabled: boolean) => void;
}

const RETRIEVER_OPTIONS: { value: RetrieverType; label: string }[] = [
  { value: 'self_query', label: 'Self Query (Default)' },
  { value: 'base', label: 'Base' },
  { value: 'multi_query', label: 'Multi Query' },
  { value: 'contextual_compression', label: 'Contextual Compression' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'ensemble', label: 'Ensemble' },
];

export function RAGSettings({
  retrieverType,
  onRetrieverTypeChange,
  useAdvancedRag,
  onAdvancedRagChange,
}: RAGSettingsProps) {
  return (
    <div className="flex flex-col gap-4 p-4 border rounded-lg bg-card">
      <h3 className="font-medium">RAG Settings</h3>

      <div className="flex flex-col gap-2">
        <Label htmlFor="retriever-type">Retriever Type</Label>
        <Select
          value={retrieverType}
          onValueChange={(value) => onRetrieverTypeChange(value as RetrieverType)}
        >
          <SelectTrigger
            id="retriever-type"
            data-testid="retriever-type-select"
          >
            <SelectValue placeholder="Select retriever type" />
          </SelectTrigger>
          <SelectContent>
            {RETRIEVER_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center justify-between">
        <Label htmlFor="advanced-rag">Advanced RAG</Label>
        <Switch
          id="advanced-rag"
          data-testid="advanced-rag-switch"
          checked={useAdvancedRag}
          onCheckedChange={onAdvancedRagChange}
        />
      </div>

      {useAdvancedRag && (
        <p className="text-xs text-muted-foreground">
          Advanced RAG uses ensemble retrieval for better results.
        </p>
      )}
    </div>
  );
}
