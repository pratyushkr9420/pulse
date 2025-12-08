# Pulse Testing Strategy

## Coverage Target: 80%

## 5-Layer Testing Pyramid

### Layer 1: Unit Tests

**Frontend (Vitest)**
- Components (isolated)
- Hooks
- Store logic
- Utility functions
- Schema validation

**Backend (pytest)**
- Service functions
- Security utilities
- Schema validation
- RAG chain components

### Layer 2: Integration Tests

**Frontend (Vitest + MSW)**
- Component + API interactions
- Form submissions

**Backend (pytest + testcontainers)**
- Database operations (PostgreSQL)
- Cache operations (Redis)
- Vector store operations (Qdrant)

### Layer 3: API Contract Tests
**Framework**: pytest + httpx

- Endpoint request/response validation
- Authentication flows
- Error handling

### Layer 4: E2E Tests

**Frontend (Playwright)**
- Browsers: chromium, firefox, webkit
- User registration flow
- User login flow
- Chat interaction
- Ticker filtering

**Backend (pytest + httpx)**
- Full request lifecycle
- Multi-step operations

### Layer 5: LLM Evaluation Tests
**Framework**: DeepEval

**Metrics**:
| Metric | Threshold | Description |
|--------|-----------|-------------|
| AnswerRelevancy | 0.7 | Does response address the financial query? |
| Faithfulness | 0.8 | Is response grounded in retrieved articles? |
| ContextualPrecision | 0.7 | Were correct articles retrieved by ticker? |
| ContextualRecall | 0.7 | Was retrieval complete? |
| Hallucination | 0.9 | Any fabricated stock information? |
| Bias | 0.8 | Is financial reporting neutral? |
| SourceCitation | 0.85 | Does response properly cite sources? |
| LinkAccuracy | 0.95 | Are links valid and accurate? |

## Running Tests

```bash
# Frontend
cd packages/frontend
npm run test:unit -- --coverage
npm run test:e2e

# Backend
cd packages/backend
uv run pytest tests/unit --cov=src
uv run pytest tests/integration
uv run pytest tests/e2e
uv run pytest tests/llm_evaluation
```

## Golden Dataset

Located at: `tests/llm_evaluation/golden_dataset.json`

Includes edge cases:
- No results found
- Unsupported ticker requests
- Partial comparison results
- Ambiguous queries
- Non-financial queries
- Follow-up questions
