"""DeepEval tests for contextual precision."""

import pytest
from deepeval import assert_test
from deepeval.metrics import ContextualPrecisionMetric


class TestContextualPrecision:
    """Test that correct articles are retrieved by ticker."""

    @pytest.fixture
    def precision_metric(self):
        return ContextualPrecisionMetric(threshold=0.5)

    @pytest.mark.asyncio
    async def test_apple_retrieval_precision(self, test_cases, precision_metric):
        """Retrieved articles for Apple query should be precise."""
        # Use test case 0: Apple news with retrieval context
        test_case = test_cases[0]
        assert_test(test_case, [precision_metric])

    @pytest.mark.asyncio
    async def test_comparison_retrieval_precision(self, test_cases, precision_metric):
        """Retrieved articles for comparison should include both tickers."""
        # Use test case 1: NVDA vs INTC comparison
        test_case = test_cases[1]
        assert_test(test_case, [precision_metric])
