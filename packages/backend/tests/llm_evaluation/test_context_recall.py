"""DeepEval tests for contextual recall."""

import pytest
from deepeval import assert_test
from deepeval.metrics import ContextualRecallMetric


class TestContextualRecall:
    """Test that retrieval is complete."""

    @pytest.fixture
    def recall_metric(self):
        return ContextualRecallMetric(threshold=0.5)

    @pytest.mark.asyncio
    async def test_apple_news_recall(self, test_cases, recall_metric):
        """Retrieval should capture all relevant Apple information."""
        # Use test case 0: Apple news with multiple context items
        test_case = test_cases[0]
        assert_test(test_case, [recall_metric])

    @pytest.mark.asyncio
    async def test_comparison_recall(self, test_cases, recall_metric):
        """Retrieval should capture information for both tickers."""
        # Use test case 1: NVDA vs INTC with both contexts
        test_case = test_cases[1]
        assert_test(test_case, [recall_metric])
