"""DeepEval test configuration and fixtures."""

import pytest
import os
from pathlib import Path

# Set up environment for DeepEval
os.environ.setdefault("DEEPEVAL_TELEMETRY", "NO")


@pytest.fixture(scope="session")
def golden_dataset():
    """Load golden dataset for evaluations."""
    import json

    dataset_path = Path(__file__).parent / "golden_dataset.json"

    with open(dataset_path, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_cases(golden_dataset):
    """Generate test cases from golden dataset.

    Creates LLMTestCase objects with all parameters from golden dataset.
    """
    from deepeval.test_case import LLMTestCase

    cases = []
    for item in golden_dataset.get("test_cases", []):
        case = LLMTestCase(
            input=item["input"],
            actual_output=item.get("actual_output", ""),
            expected_output=item.get("expected_output", ""),
            retrieval_context=item.get("retrieval_context", []),
            context=item.get("context", []),
        )
        cases.append(case)

    return cases
