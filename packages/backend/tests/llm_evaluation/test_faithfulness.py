"""DeepEval tests for faithfulness."""

import pytest
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric


class TestFaithfulness:
    """Test that responses are grounded in retrieved articles."""

    @pytest.fixture
    def faithfulness_metric(self):
        return FaithfulnessMetric(threshold=0.7)

    @pytest.mark.asyncio
    async def test_apple_news_faithfulness(self, test_cases, faithfulness_metric):
        """Apple news response should be faithful to retrieval context."""
        # Use test case 0: Apple news with retrieval context
        test_case = test_cases[0]
        assert_test(test_case, [faithfulness_metric])

    @pytest.mark.asyncio
    async def test_comparison_faithfulness(self, test_cases, faithfulness_metric):
        """Comparison response should be faithful to both sources."""
        # Use test case 1: NVDA vs INTC with multiple sources
        test_case = test_cases[1]
        assert_test(test_case, [faithfulness_metric])

    @pytest.mark.asyncio
    async def test_microsoft_cloud_faithfulness(self, test_cases, faithfulness_metric):
        """Microsoft cloud response should be faithful to context."""
        # Use test case 3: Microsoft cloud services
        test_case = test_cases[3]
        assert_test(test_case, [faithfulness_metric])
