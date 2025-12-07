"""DeepEval tests for answer relevancy."""

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric


class TestAnswerRelevancy:
    """Test that responses are relevant to financial queries."""

    @pytest.fixture
    def relevancy_metric(self):
        return AnswerRelevancyMetric(threshold=0.7)

    @pytest.mark.asyncio
    async def test_apple_news_relevancy(self, test_cases, relevancy_metric):
        """Response about Apple should be relevant to the query."""
        # Use test case 0: "What is the latest news about Apple?"
        test_case = test_cases[0]
        assert_test(test_case, [relevancy_metric])

    @pytest.mark.asyncio
    async def test_comparison_query_relevancy(self, test_cases, relevancy_metric):
        """Response comparing NVDA and INTC should be relevant."""
        # Use test case 1: "Compare NVDA and INTC"
        test_case = test_cases[1]
        assert_test(test_case, [relevancy_metric])

    @pytest.mark.asyncio
    async def test_microsoft_cloud_relevancy(self, test_cases, relevancy_metric):
        """Response about Microsoft cloud should be relevant."""
        # Use test case 3: "Tell me about Microsoft cloud services"
        test_case = test_cases[3]
        assert_test(test_case, [relevancy_metric])

    @pytest.mark.asyncio
    async def test_multi_stock_relevancy(self, test_cases, relevancy_metric):
        """Response about Amazon and Netflix should be relevant."""
        # Use test case 4: "What's happening with Amazon and Netflix?"
        test_case = test_cases[4]
        assert_test(test_case, [relevancy_metric])
