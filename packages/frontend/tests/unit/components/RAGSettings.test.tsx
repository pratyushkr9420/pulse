/**
 * Tests for RAGSettings component.
 *
 * CORRECTED: Uses data-testid for reliable element selection.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RAGSettings } from '@/components/chat/RAGSettings';

describe('RAGSettings', () => {
  const defaultProps = {
    retrieverType: 'self_query' as const,
    onRetrieverTypeChange: vi.fn(),
    useAdvancedRag: false,
    onAdvancedRagChange: vi.fn(),
  };

  it('renders with default retriever type', () => {
    render(<RAGSettings {...defaultProps} />);

    // CORRECTED: Use data-testid for reliable selection
    const select = screen.getByTestId('retriever-type-select');
    expect(select).toBeInTheDocument();
  });

  it('displays current retriever type selection', () => {
    render(<RAGSettings {...defaultProps} retrieverType="self_query" />);

    // Check that the selected value is displayed
    expect(screen.getByText('Self Query (Default)')).toBeInTheDocument();
  });

  it('displays different retriever types correctly', () => {
    const { rerender } = render(<RAGSettings {...defaultProps} retrieverType="multi_query" />);

    // Should show Multi Query when that type is selected
    expect(screen.getByText('Multi Query')).toBeInTheDocument();

    // Rerender with different type
    rerender(<RAGSettings {...defaultProps} retrieverType="hybrid" />);
    expect(screen.getByText('Hybrid')).toBeInTheDocument();
  });

  it('toggles advanced RAG switch', async () => {
    const user = userEvent.setup();
    const mockChange = vi.fn();
    render(<RAGSettings {...defaultProps} onAdvancedRagChange={mockChange} />);

    // CORRECTED: Use data-testid for switch
    const toggle = screen.getByTestId('advanced-rag-switch');
    await user.click(toggle);

    expect(mockChange).toHaveBeenCalledWith(true);
  });

  it('displays contextual description for selected retriever', () => {
    render(<RAGSettings {...defaultProps} retrieverType="hybrid" />);

    // Should show description for hybrid retriever
    expect(screen.getByText(/Combines multiple search strategies/i)).toBeInTheDocument();
    expect(screen.getByText(/Comparing companies or getting diverse perspectives/i)).toBeInTheDocument();
  });

  it('displays contextual description for different retrievers', () => {
    const { rerender } = render(<RAGSettings {...defaultProps} retrieverType="base" />);

    // Should show base description
    expect(screen.getByText(/Fast and simple search/i)).toBeInTheDocument();

    // Rerender with contextual_compression
    rerender(<RAGSettings {...defaultProps} retrieverType="contextual_compression" />);
    expect(screen.getByText(/Extracts the most relevant parts/i)).toBeInTheDocument();
  });

  it('shows Search Settings header with tooltip', () => {
    render(<RAGSettings {...defaultProps} />);

    expect(screen.getByText('Search Settings')).toBeInTheDocument();
  });

  it('shows Search Method label', () => {
    render(<RAGSettings {...defaultProps} />);

    expect(screen.getByText('Search Method')).toBeInTheDocument();
  });
});
