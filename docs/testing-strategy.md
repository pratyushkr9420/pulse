# Pulse Testing Strategy

## Overview

Pulse implements a comprehensive **5-layer testing pyramid** with **39 total test files** across backend and frontend. The testing strategy ensures production readiness through unit, integration, E2E, and specialized LLM evaluation tests.

## Coverage Target

**Minimum**: 80% code coverage across all layers
**Current**: ~85% backend, ~82% frontend

## Test Suite Summary

| Layer | Backend | Frontend | Total | Framework |
|-------|---------|----------|-------|-----------|
| **Unit** | 15 | 10 | **25** | pytest, Vitest |
| **Integration** | 3 | 0 | **3** | pytest + testcontainers |
| **E2E** | 1 | 2 | **3** | pytest, Playwright |
| **LLM Evaluation** | 8 | 0 | **8** | DeepEval |
| **Total** | **27** | **12** | **39** | - |

---

## 5-Layer Testing Pyramid

### Layer 1: Unit Tests (25 files)

Unit tests verify isolated functionality of individual components, functions, and classes.

#### Backend Unit Tests (15 files)

**Location**: `packages/backend/tests/unit/`

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_chain.py` | RAG chain | LCEL chain composition, prompt formatting |
| `test_config.py` | Configuration | Environment variable loading, validation |
| `test_data_loader.py` | Document loading | JSON parsing, metadata extraction |
| `test_database.py` | Database models | ORM model validation, relationships |
| `test_db_session.py` | DB sessions | Async session factory, connection pooling |
| `test_embeddings.py` | Embeddings | OpenAI embedding generation, caching |
| `test_exceptions.py` | Error handling | Custom exception classes, error propagation |
| `test_logging.py` | Logging | Structured logging, log levels |
| `test_models.py` | ORM models | User, ChatHistory model validation |
| `test_retrievers.py` | Retrievers | All 6 retriever types, factory pattern |
| `test_schemas.py` | Pydantic schemas | Request/response validation |
| `test_security.py` | Auth utilities | JWT token creation, password hashing |
| `test_services.py` | Business logic | Auth service, chat service |
| `test_utils.py` | Helper functions | Utility functions, formatters |
| `test_vector_store.py` | Qdrant | Vector store operations, hybrid search |

**Run backend unit tests**:
```bash
cd packages/backend
uv run pytest tests/unit/ -v --cov=src --cov-report=html
```

#### Frontend Unit Tests (10 files)

**Location**: `packages/frontend/tests/unit/components/`

| Test File | Component | Tests |
|-----------|-----------|-------|
| `ChatContainer.test.tsx` | ChatContainer | Message rendering, scroll behavior |
| `ChatInput.test.tsx` | ChatInput | Input validation, submission, loading state |
| `ChatMessage.test.tsx` | ChatMessage | Message display, user/assistant styling |
| `GroupedSourcesList.test.tsx` | GroupedSourcesList | Source grouping by ticker, collapsing |
| `LoginForm.test.tsx` | LoginForm | Form validation, submission, error handling |
| `RAGSettings.test.tsx` | RAGSettings | Retriever selection, k/threshold sliders |
| `RegisterForm.test.tsx` | RegisterForm | Password matching, validation |
| `SourceCard.test.tsx` | SourceCard | Source rendering, link display |
| `SourcesList.test.tsx` | SourcesList | Source list rendering, empty state |
| `TickerFilter.test.tsx` | TickerFilter | Ticker selection, multi-select |

**Run frontend unit tests**:
```bash
cd packages/frontend
npm run test:unit -- --coverage
```

**Mocking Strategy**: Uses `vi.fn()` from Vitest for mocking API calls, stores, and hooks.

---

### Layer 2: Integration Tests (3 files)

Integration tests verify interactions between multiple components, databases, and external services.

#### Backend Integration Tests (3 files)

**Location**: `packages/backend/tests/integration/`

| Test File | Integration Scope | Dependencies |
|-----------|------------------|--------------|
| `test_auth_routes.py` | Auth endpoints + PostgreSQL | Database, JWT tokens |
| `test_chat_routes.py` | Chat endpoints + Qdrant + Redis | Vector DB, cache, auth |
| `test_db.py` | Database operations | PostgreSQL, migrations |

**Infrastructure**: Uses **testcontainers** to spin up real PostgreSQL, Redis, and Qdrant containers during tests.

**Run backend integration tests**:
```bash
cd packages/backend
uv run pytest tests/integration/ -v
```

**Note**: Requires Docker to be running.

#### Frontend Integration Tests

**Status**: Not implemented (covered by E2E tests instead)

**Rationale**: E2E tests with real API calls provide more realistic integration testing than MSW mocks.

---

### Layer 3: API Contract Tests

**Embedded in Integration Tests**: Backend integration tests (`test_auth_routes.py`, `test_chat_routes.py`) validate API contracts.

**Validation**:
- Request schema validation (Pydantic)
- Response schema validation
- HTTP status codes
- Error response formats

**Framework**: pytest + httpx

---

### Layer 4: E2E Tests (3 files)

E2E tests verify complete user workflows across the entire application stack.

#### Backend E2E Tests (1 file)

**Location**: `packages/backend/tests/e2e/`

| Test File | Workflow | Description |
|-----------|----------|-------------|
| `test_full_flow.py` | Complete RAG flow | Register → Login → Ask question → Verify sources |

**Run backend E2E tests**:
```bash
cd packages/backend
uv run pytest tests/e2e/ -v
```

#### Frontend E2E Tests (2 files)

**Location**: `packages/frontend/tests/e2e/`

**Framework**: Playwright (chromium, firefox, webkit)

| Test File | Test Cases | Description |
|-----------|------------|-------------|
| `auth.spec.ts` | 5 tests | Register, login, protected routes, invalid credentials, logout |
| `chat.spec.ts` | 5 tests | Send message, display sources, filter by ticker, change retriever, chat history |

**Run frontend E2E tests**:
```bash
cd packages/frontend
npm run test:e2e
```

**Test Strategy**:
- Uses **real backend API** (not mocked)
- Tests run against local development server
- Unique usernames generated per test run to avoid conflicts
- Waits for async operations with explicit timeouts

**Example E2E test** (`chat.spec.ts:19-26`):
```typescript
test('can send a message', async ({ page }) => {
  await page.fill('textarea[placeholder="Ask about stock news..."]',
    'What is the latest AAPL news?');
  await page.click('button[type="submit"]');

  // Wait for response
  await expect(page.locator('text=AAPL').first())
    .toBeVisible({ timeout: 15000 });
});
```

---

### Layer 5: LLM Evaluation Tests (8 files)

Specialized tests for evaluating RAG quality using DeepEval metrics.

**Location**: `packages/backend/tests/llm_evaluation/`

**Framework**: DeepEval (LLM-based evaluation)

#### Evaluation Metrics

| Test File | Metric | Threshold | Description |
|-----------|--------|-----------|-------------|
| `test_answer_relevancy.py` | AnswerRelevancy | 0.7 | Does response address the financial query? |
| `test_faithfulness.py` | Faithfulness | 0.8 | Is response grounded in retrieved articles? |
| `test_context_precision.py` | ContextPrecision | 0.7 | Were correct articles retrieved by ticker? |
| `test_context_recall.py` | ContextRecall | 0.7 | Was retrieval complete? |
| `test_hallucination.py` | Hallucination | 0.9 | Any fabricated stock information? |
| `test_bias.py` | Bias | 0.8 | Is financial reporting neutral? |
| `test_source_citation.py` | SourceCitation | 0.85 | Does response properly cite sources? |
| `test_link_accuracy.py` | LinkAccuracy | 0.95 | Are links valid and accurate? |

**Run LLM evaluation tests**:
```bash
cd packages/backend
uv run pytest tests/llm_evaluation/ -v
```

**Golden Dataset**: `tests/llm_evaluation/golden_dataset.json`

**Test cases include**:
- Normal retrieval scenarios (AAPL, MSFT, AMZN)
- Edge cases (no results, unsupported tickers)
- Comparison queries (AAPL vs MSFT)
- Ambiguous queries
- Non-financial questions
- Follow-up questions

**Example evaluation**:
```python
@pytest.mark.asyncio
async def test_answer_relevancy():
    test_case = LLMTestCase(
        input="What is the latest Apple news?",
        actual_output=response,
        retrieval_context=sources
    )
    metric = AnswerRelevancyMetric(threshold=0.7)
    await metric.a_measure(test_case)
    assert metric.score >= 0.7
```

---

## Running All Tests

### Using Makefile (Recommended)

```bash
# Run all tests (backend + frontend)
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run with coverage reports
make test-coverage
```

### Manual Commands

#### Backend Tests

```bash
cd packages/backend

# All backend tests
uv run pytest -v

# Unit tests only
uv run pytest tests/unit/ -v --cov=src --cov-report=html

# Integration tests (requires Docker)
uv run pytest tests/integration/ -v

# E2E tests
uv run pytest tests/e2e/ -v

# LLM evaluation tests
uv run pytest tests/llm_evaluation/ -v

# Specific test file
uv run pytest tests/unit/test_retrievers.py -v

# Coverage report (HTML)
uv run pytest tests/unit --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

#### Frontend Tests

```bash
cd packages/frontend

# Unit tests
npm run test:unit

# Unit tests with coverage
npm run test:unit -- --coverage

# E2E tests (requires backend running)
npm run test:e2e

# E2E tests in headed mode (see browser)
npm run test:e2e -- --headed

# E2E tests in specific browser
npm run test:e2e -- --project=firefox

# Watch mode for development
npm run test:unit -- --watch
```

---

## Test Configuration Files

### Backend Configuration

**pytest.ini** (or `pyproject.toml` pytest section):
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "llm_eval: LLM evaluation tests"
]
```

**Coverage Configuration** (`.coveragerc` or `pyproject.toml`):
```ini
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError"
]
```

### Frontend Configuration

**vitest.config.ts**:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['**/node_modules/**', '**/e2e/**', 'tests/e2e/**'],
    coverage: {
      provider: 'istanbul',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/', '**/*.d.ts', '**/*.config.*']
    }
  }
});
```

**playwright.config.ts**:
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Continuous Integration

Tests run automatically on GitHub Actions for every pull request.

**Workflow**: `.github/workflows/ci.yml`

### CI Pipeline Stages

1. **Lint** (Backend + Frontend)
   - Ruff (Python)
   - ESLint (TypeScript)

2. **Unit Tests** (Parallel)
   - Backend unit tests with coverage
   - Frontend unit tests with coverage

3. **Integration Tests** (Backend)
   - Spins up Docker containers
   - Runs integration tests
   - Tears down containers

4. **E2E Tests** (Frontend)
   - Starts backend + frontend
   - Runs Playwright tests
   - Captures screenshots on failure

5. **LLM Evaluation** (Weekly)
   - Runs DeepEval metrics
   - Reports metric scores
   - Alerts if below threshold

**Badge**: ![Tests](https://github.com/user/pulse/workflows/tests/badge.svg)

---

## Testing Best Practices

### 1. Test Naming Convention

```python
# Backend
def test_create_retriever_with_self_query_type():
    """Test that self_query retriever is created correctly."""
    pass

# Frontend
test('should display error message on invalid login', async () => {
    // ...
});
```

### 2. Arrange-Act-Assert Pattern

```python
def test_password_hashing():
    # Arrange
    password = "securePassword123"

    # Act
    hashed = hash_password(password)

    # Assert
    assert verify_password(password, hashed)
    assert hashed != password
```

### 3. Fixtures for Test Data

```python
# conftest.py
@pytest.fixture
async def test_user():
    """Create a test user."""
    user = User(username="testuser", password="testpass")
    yield user
    # Cleanup
    await delete_user(user.id)
```

### 4. Mock External Services

```python
# Mock OpenAI API
@patch('openai.Embedding.create')
def test_embeddings(mock_embed):
    mock_embed.return_value = {"data": [{"embedding": [0.1] * 1536}]}
    embeddings = get_embeddings("test text")
    assert len(embeddings) == 1536
```

### 5. Test Edge Cases

```python
# Test empty input
def test_chat_with_empty_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="")

# Test maximum input
def test_chat_with_max_length_message():
    message = "a" * 1000
    request = ChatRequest(message=message)
    assert len(request.message) == 1000
```

---

## Test Data Management

### Golden Dataset (`tests/llm_evaluation/golden_dataset.json`)

**Structure**:
```json
[
  {
    "input": "What is the latest Apple news?",
    "expected_context": ["AAPL"],
    "expected_tickers": ["AAPL"],
    "category": "normal_query"
  },
  {
    "input": "Tell me about a company not in our dataset",
    "expected_context": [],
    "expected_tickers": [],
    "category": "edge_case_no_results"
  }
]
```

**Categories**:
- `normal_query`: Standard retrieval
- `edge_case_no_results`: No matching articles
- `edge_case_unsupported_ticker`: Ticker not in dataset
- `comparison_query`: Multiple tickers
- `ambiguous_query`: Unclear intent
- `non_financial`: Off-topic question
- `follow_up`: Contextual question

---

## Debugging Failed Tests

### Backend Test Failures

```bash
# Run with verbose output
uv run pytest tests/unit/test_retrievers.py -vv

# Run with print statements
uv run pytest tests/unit/test_retrievers.py -s

# Run with debugger (drops into pdb on failure)
uv run pytest tests/unit/test_retrievers.py --pdb

# Show local variables on failure
uv run pytest tests/unit/test_retrievers.py -l
```

### Frontend Test Failures

```bash
# Run in UI mode (Vitest)
npm run test:unit -- --ui

# Run with debugger
npm run test:unit -- --inspect-brk

# E2E with screenshots
npm run test:e2e -- --screenshot=on

# E2E with video
npm run test:e2e -- --video=on
```

---

## Performance Testing

### Load Testing (Optional)

Use **Locust** for API load testing:

```python
# locustfile.py
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def send_message(self):
        self.client.post("/api/v1/chat", json={
            "message": "What is the latest AAPL news?",
            "retriever_type": "self_query"
        }, headers={"Authorization": f"Bearer {self.token}"})
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Test Metrics

### Current Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| Backend API | 87% | ✅ |
| Backend RAG | 92% | ✅ |
| Backend Services | 85% | ✅ |
| Frontend Components | 82% | ✅ |
| Frontend Hooks | 78% | ⚠️ |

### Test Execution Time

| Layer | Time | Files |
|-------|------|-------|
| Backend Unit | ~15s | 15 |
| Backend Integration | ~45s | 3 |
| Backend E2E | ~30s | 1 |
| LLM Evaluation | ~120s | 8 |
| Frontend Unit | ~8s | 10 |
| Frontend E2E | ~60s | 2 |
| **Total** | **~4.5min** | **39** |

---

## Troubleshooting

### Common Issues

#### 1. Docker containers not starting (Integration tests)

```bash
# Check Docker is running
docker ps

# Pull required images
docker pull postgres:16-alpine
docker pull redis:7-alpine
docker pull qdrant/qdrant:latest
```

#### 2. OpenAI API key not set (LLM evaluation)

```bash
# Set in .env file
OPENAI_API_KEY=sk-your-key-here

# Or export
export OPENAI_API_KEY=sk-your-key-here
```

#### 3. Frontend E2E tests timing out

```typescript
// Increase timeout in individual test
test('slow test', async ({ page }) => {
  test.setTimeout(60000);  // 60 seconds
  // ... test code
});

// Or set default timeout for all tests in playwright.config.ts
export default defineConfig({
  // ... other config
  timeout: 60000,  // 60 seconds for all tests
});
```

#### 4. Database migration errors (Integration tests)

```bash
# Reset test database
uv run alembic downgrade base
uv run alembic upgrade head
```

---

## Future Testing Enhancements

### Planned Improvements

1. **Visual Regression Testing**
   - Add Percy or Chromatic for UI snapshot testing
   - Detect unintended visual changes

2. **Contract Testing**
   - Add Pact for consumer-driven contract tests
   - Ensure API compatibility across versions

3. **Mutation Testing**
   - Use mutmut (Python) to verify test quality
   - Ensure tests catch all code changes

4. **Performance Benchmarks**
   - Add pytest-benchmark for RAG pipeline
   - Track performance regressions over time

5. **Security Testing**
   - Add bandit (Python) and npm audit
   - Scan for vulnerabilities in dependencies

---

## Summary

Pulse's 5-layer testing pyramid ensures:

✅ **39 total test files** covering all critical paths
✅ **~85% code coverage** across backend and frontend
✅ **Real integration tests** with Docker containers
✅ **E2E tests** with real backend API (no mocks)
✅ **8 LLM evaluation metrics** for RAG quality
✅ **CI/CD integration** on every pull request

**Testing Philosophy**: Write tests that provide confidence, not just coverage.
