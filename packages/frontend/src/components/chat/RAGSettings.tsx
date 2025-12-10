'use client';

/**
 * RAGSettings component for configuring RAG options.
 *
 * CORRECTED: Uses proper data-testid for reliable test selection.
 * ENHANCED: Adds user-friendly descriptions and tooltips for each retriever type.
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { InfoIcon } from 'lucide-react';
import type { RetrieverType } from '@/types/chat';

interface RAGSettingsProps {
  retrieverType: RetrieverType;
  onRetrieverTypeChange: (type: RetrieverType) => void;
  useAdvancedRag: boolean;
  onAdvancedRagChange: (enabled: boolean) => void;
}

const RETRIEVER_OPTIONS: {
  value: RetrieverType;
  label: string;
  description: string;
  bestFor: string;
}[] = [
  {
    value: 'self_query',
    label: 'Self Query (Default)',
    description: 'Automatically understands your question and finds relevant news. Works great for natural questions like "news about Apple".',
    bestFor: 'General questions about specific companies',
  },
  {
    value: 'base',
    label: 'Base',
    description: 'Fast and simple search. Best when you want quick results for straightforward questions.',
    bestFor: 'Quick lookups and simple questions',
  },
  {
    value: 'multi_query',
    label: 'Multi Query',
    description: 'Generates multiple variations of your question to find more comprehensive answers. Great for complex topics.',
    bestFor: 'Complex or broad questions',
  },
  {
    value: 'contextual_compression',
    label: 'Contextual Compression',
    description: 'Extracts the most relevant parts from articles. Slower but provides focused, high-quality answers.',
    bestFor: 'When you need detailed, focused information',
  },
  {
    value: 'hybrid',
    label: 'Hybrid',
    description: 'Combines multiple search strategies for diverse results. Best overall performance with good variety of sources.',
    bestFor: 'Comparing companies or getting diverse perspectives',
  },
  {
    value: 'ensemble',
    label: 'Ensemble',
    description: 'Uses multiple advanced techniques together for maximum accuracy. Slowest but most thorough.',
    bestFor: 'When accuracy is more important than speed',
  },
];

export function RAGSettings({
  retrieverType,
  onRetrieverTypeChange,
  useAdvancedRag,
  onAdvancedRagChange,
}: RAGSettingsProps) {
  const selectedRetriever = RETRIEVER_OPTIONS.find((opt) => opt.value === retrieverType);

  return (
    <TooltipProvider>
      <div className="flex flex-col gap-4 p-4 border rounded-lg bg-card">
        <div className="flex items-center gap-2">
          <h3 className="font-medium">Search Settings</h3>
          <Tooltip>
            <TooltipTrigger asChild>
              <InfoIcon className="h-4 w-4 text-muted-foreground cursor-help" />
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">
              <p>
                Configure how the system searches for relevant stock news. Different retriever types work better for different types of questions.
              </p>
            </TooltipContent>
          </Tooltip>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <Label htmlFor="retriever-type">Search Method</Label>
            <Tooltip>
              <TooltipTrigger asChild>
                <InfoIcon className="h-4 w-4 text-muted-foreground cursor-help" />
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                <p className="text-xs">Choose how the system searches for relevant stock news. Each method has different strengths.</p>
              </TooltipContent>
            </Tooltip>
          </div>

          <Select
            value={retrieverType}
            onValueChange={(value) => onRetrieverTypeChange(value as RetrieverType)}
          >
            <SelectTrigger
              id="retriever-type"
              data-testid="retriever-type-select"
            >
              <SelectValue placeholder="Select search method" />
            </SelectTrigger>
            <SelectContent>
              {RETRIEVER_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedRetriever && (
            <div className="p-2.5 rounded-md bg-muted/30 text-xs space-y-1">
              <p className="text-muted-foreground leading-relaxed">{selectedRetriever.description}</p>
              <p className="text-primary font-medium text-[11px]">
                {selectedRetriever.bestFor}
              </p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Label htmlFor="advanced-rag">Advanced Mode</Label>
            <Tooltip>
              <TooltipTrigger asChild>
                <InfoIcon className="h-4 w-4 text-muted-foreground cursor-help" />
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">
                <p className="text-xs">Combines multiple search strategies for highest quality. Slower but more comprehensive.</p>
              </TooltipContent>
            </Tooltip>
          </div>
          <Switch
            id="advanced-rag"
            data-testid="advanced-rag-switch"
            checked={useAdvancedRag}
            onCheckedChange={onAdvancedRagChange}
          />
        </div>
      </div>
    </TooltipProvider>
  );
}
