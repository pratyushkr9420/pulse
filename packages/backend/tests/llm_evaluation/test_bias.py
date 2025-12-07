"""DeepEval tests for bias detection."""

import pytest
from deepeval import assert_test
from deepeval.metrics import BiasMetric


class TestBias:
    """Test that financial reporting is neutral."""

    @pytest.fixture
    def bias_metric(self):
        return BiasMetric(threshold=0.8)

    @pytest.mark.asyncio
    async def test_comparison_neutrality(self, test_cases, bias_metric):
        """Comparison of NVDA and INTC should be neutral."""
        # Use test case 1: NVDA vs INTC - should present facts neutrally
        test_case = test_cases[1]
        assert_test(test_case, [bias_metric])

    @pytest.mark.asyncio
    async def test_no_investment_advice(self, test_cases, bias_metric):
        """Response should decline giving investment advice without bias."""
        # Use test case 6: "Should I buy Apple stock?" - neutral refusal
        test_case = test_cases[6]
        assert_test(test_case, [bias_metric])

    @pytest.mark.asyncio
    async def test_factual_news_reporting(self, test_cases, bias_metric):
        """News reporting should be factual and unbiased."""
        # Use test case 0: Apple news - factual reporting
        test_case = test_cases[0]
        assert_test(test_case, [bias_metric])
