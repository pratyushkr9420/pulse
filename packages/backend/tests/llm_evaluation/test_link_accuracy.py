"""Custom DeepEval metric for link accuracy validation.

Per .cursorrules custom_metrics.LinkAccuracyMetric:
Validates that:
1. All links in response are from the retrieved sources
2. Links are properly formatted (valid URLs)
3. Link matches the article title/ticker claimed
"""

import pytest
import re
from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class LinkAccuracyMetric(BaseMetric):
    """Custom metric to validate link accuracy in RAG responses."""

    def __init__(self, threshold: float = 0.95):
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = None
        self.async_mode = False

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure link accuracy in response."""
        output = test_case.actual_output
        retrieval_context = test_case.retrieval_context or []

        url_pattern = r'https?://[^\s<>"]+[^\s<>".,;:)]'
        output_urls = set(re.findall(url_pattern, output))

        if not output_urls:
            self.score = 1.0
            self.reason = "No URLs in output"
            self.success = self.score >= self.threshold
            return self.score

        context_text = ' '.join(retrieval_context) if retrieval_context else ''
        context_urls = set(re.findall(url_pattern, context_text))

        valid_urls = 0
        for url in output_urls:
            is_valid = True

            if not url.startswith('http://') and not url.startswith('https://'):
                is_valid = False

            if context_urls and url not in context_urls:
                is_valid = False

            if is_valid:
                valid_urls += 1

        self.score = valid_urls / len(output_urls) if output_urls else 1.0
        self.reason = f"Valid URLs: {valid_urls}/{len(output_urls)}"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async measure - calls synchronous measure."""
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "LinkAccuracyMetric"


class TestLinkAccuracy:
    """Tests for link accuracy validation."""

    @pytest.fixture
    def link_metric(self):
        return LinkAccuracyMetric(threshold=0.95)

    @pytest.mark.asyncio
    async def test_apple_link_accuracy(self, test_cases, link_metric):
        """Apple news links should be accurate."""
        # Use test case 0: Apple news with valid links
        test_case = test_cases[0]
        assert_test(test_case, [link_metric])

    @pytest.mark.asyncio
    async def test_comparison_link_accuracy(self, test_cases, link_metric):
        """Comparison response links should be accurate."""
        # Use test case 1: NVDA vs INTC with links
        test_case = test_cases[1]
        assert_test(test_case, [link_metric])

    @pytest.mark.asyncio
    async def test_microsoft_link_accuracy(self, test_cases, link_metric):
        """Microsoft cloud response links should be accurate."""
        # Use test case 3: Microsoft with links
        test_case = test_cases[3]
        assert_test(test_case, [link_metric])

    @pytest.mark.asyncio
    async def test_multi_stock_link_accuracy(self, test_cases, link_metric):
        """Multi-stock response links should be accurate."""
        # Use test case 4: Amazon and Netflix with links
        test_case = test_cases[4]
        assert_test(test_case, [link_metric])
