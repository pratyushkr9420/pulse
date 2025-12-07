"""DeepEval tests for hallucination detection."""

import pytest
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric


class TestHallucination:
    """Test that responses don't contain hallucinations."""

    @pytest.fixture
    def hallucination_metric(self):
        return HallucinationMetric(threshold=0.7)

    @pytest.mark.asyncio
    async def test_grounded_apple_response(self, test_cases, hallucination_metric):
        """Apple response should not hallucinate information."""
        # Use test case 0: Apple news grounded in context
        test_case = test_cases[0]
        assert_test(test_case, [hallucination_metric])

    @pytest.mark.asyncio
    async def test_no_investment_advice_hallucination(self, test_cases, hallucination_metric):
        """Response declining investment advice should not hallucinate."""
        # Use test case 6: "Should I buy Apple stock?" - responds without hallucinating advice
        test_case = test_cases[6]
        assert_test(test_case, [hallucination_metric])

    @pytest.mark.asyncio
    async def test_stock_price_limitation_no_hallucination(self, test_cases, hallucination_metric):
        """Response about stock price limitation should not hallucinate prices."""
        # Use test case 7: "What is Apple's current stock price?" - states limitation
        test_case = test_cases[7]
        assert_test(test_case, [hallucination_metric])
