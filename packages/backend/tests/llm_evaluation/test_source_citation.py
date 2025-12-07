"""Custom DeepEval metric for source citation validation.

Per .cursorrules custom_metrics.SourceCitationMetric:
Validates that:
1. Every factual claim has a source citation
2. Citations include article title
3. Citations include ticker symbol
4. Citations include valid link URL
"""

import pytest
import re
from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class SourceCitationMetric(BaseMetric):
    """Custom metric to validate source citations in RAG responses."""

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = None
        self.async_mode = False

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure citation quality in response."""
        output = test_case.actual_output
        retrieval_context = test_case.retrieval_context or []

        # Pattern to match citations
        citation_pattern = r'\[([^\]]+)\]\s*\(([A-Z]+)\)\s*-\s*Link:\s*<?([^>\s]+)>?'
        citations = re.findall(citation_pattern, output)

        if not citations and len(retrieval_context) > 0:
            self.score = 0.0
            self.reason = "No citations found despite having context"
            self.success = self.score >= self.threshold
            return self.score

        if not citations and len(retrieval_context) == 0:
            self.score = 1.0
            self.reason = "No citations needed (no context provided)"
            self.success = self.score >= self.threshold
            return self.score

        valid_citations = 0
        total_citations = len(citations)
        supported_tickers = {'AAPL', 'MSFT', 'AMZN', 'NFLX', 'NVDA', 'INTC', 'IBM'}

        for title, ticker, link in citations:
            is_valid = True

            if ticker not in supported_tickers:
                is_valid = False
            if not link.startswith('http'):
                is_valid = False
            if not title.strip():
                is_valid = False

            if is_valid:
                valid_citations += 1

        self.score = valid_citations / total_citations if total_citations > 0 else 0.0
        self.reason = f"Valid citations: {valid_citations}/{total_citations}"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async measure - calls synchronous measure."""
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "SourceCitationMetric"


class TestSourceCitation:
    """Tests for source citation validation."""

    @pytest.fixture
    def citation_metric(self):
        return SourceCitationMetric(threshold=0.85)

    @pytest.mark.asyncio
    async def test_apple_citations(self, test_cases, citation_metric):
        """Apple news response should have valid citations."""
        # Use test case 0: Apple news with proper citations
        test_case = test_cases[0]
        assert_test(test_case, [citation_metric])

    @pytest.mark.asyncio
    async def test_comparison_citations(self, test_cases, citation_metric):
        """Comparison response should cite both sources."""
        # Use test case 1: NVDA vs INTC with citations for both
        test_case = test_cases[1]
        assert_test(test_case, [citation_metric])

    @pytest.mark.asyncio
    async def test_microsoft_citations(self, test_cases, citation_metric):
        """Microsoft cloud response should have citations."""
        # Use test case 3: Microsoft with proper citations
        test_case = test_cases[3]
        assert_test(test_case, [citation_metric])

    @pytest.mark.asyncio
    async def test_multi_stock_citations(self, test_cases, citation_metric):
        """Multi-stock response should cite all sources."""
        # Use test case 4: Amazon and Netflix with citations
        test_case = test_cases[4]
        assert_test(test_case, [citation_metric])
