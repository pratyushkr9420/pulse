# Pulse Architecture

## Overview

Pulse is a production-ready RAG-based financial news query system that allows users to ask questions about tech stocks (AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM) and receive answers with cited sources. The system features 6 retriever types, hybrid search capability, comprehensive observability, and enterprise-grade security.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Layer                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Frontend (Next.js 15 App Router)                             │  │
│  │  - React 19, TypeScript 5.7                                   │  │
│  │  - TanStack Query v5 (server state)                           │  │
│  │  - Zustand v5 (client state)                                  │  │
│  │  - shadcn/ui components                                       │  │
│  │  - Zod validation                                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/REST (JWT Auth)
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Application Layer                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Backend API (FastAPI)                                        │  │
│  │  - Python 3.12, uv package manager                            │  │
│  │  - Pydantic v2 validation                                     │  │
│  │  - JWT authentication (python-jose + passlib)                 │  │
│  │  - Rate limiting (SlowAPI)                                    │  │
│  │  - CORS, logging, exception handling                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  RAG Pipeline (LangChain LCEL - NO LangGraph)                │  │
│  │  - 6 retriever types via factory pattern                      │  │
│  │  - Hybrid search (dense + sparse vectors)                     │  │
│  │  - Self-query with metadata filtering                         │  │
│  │  - Contextual compression                                     │  │
│  │  - Ensemble retrieval                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Data & Services Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ PostgreSQL   │  │    Redis     │  │   Qdrant     │             │
│  │   (v16)      │  │    (v7)      │  │ (Vector DB)  │             │
│  │              │  │              │  │              │             │
│  │ - Users      │  │ - Cache      │  │ - Embeddings │             │
│  │ - Chat Hist. │  │ - Sessions   │  │ - Metadata   │             │
│  │ - SQLAlchemy │  │ - Rate limit │  │ - Hybrid idx │             │
│  │ - Alembic    │  │              │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External Services                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  OpenAI API  │  │  LangSmith   │  │    Sentry    │             │
│  │              │  │              │  │              │             │
│  │ - gpt-4o-mini│  │ - Tracing    │  │ - Errors     │             │
│  │ - Embeddings │  │ - Monitoring │  │ - Perf       │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Decisions

### NO LangGraph
We use LangChain LCEL instead of LangGraph because:
- This is a straightforward RAG application
- No multi-agent coordination needed
- No complex state management required
- LCEL provides clean, composable chains

### OpenAI Models
- **Chat**: gpt-4o-mini (cost-effective, fast)
- **Embeddings**: text-embedding-3-small (1536 dimensions)

### Qdrant Vector Store
- Superior metadata filtering for ticker-based queries
- Local development mode with Docker
- Production-ready with cloud hosting
- Supports hybrid search (dense + sparse)

## RAG Pipeline Details

### 1. Document Loading (`src/rag/data_loader.py`)
- **Data source**: `packages/backend/data/stock_news.json` (138 articles, 7 tickers, 585KB)
- **Loader**: JSONLoader from langchain_community
- **Schema**: Each article has title, link, ticker, full_text
- **Jq schema**: `.[] | {title, link, ticker, full_text}`

### 2. Text Splitting
- **Splitter**: RecursiveCharacterTextSplitter
- **Chunk size**: 1000 characters
- **Overlap**: 200 characters
- **Metadata preservation**: ticker, title, link attached to each chunk

### 3. Embedding (`src/rag/embeddings.py`)
- **Model**: OpenAI text-embedding-3-small
- **Dimensions**: 1536
- **Singleton pattern**: @lru_cache for reuse across requests
- **Rate limiting**: OpenAI default (3000 RPM)

### 4. Vector Storage (`src/rag/vector_store.py`)
- **Database**: Qdrant (local Docker or cloud)
- **Collection name**: stock_news (configurable)
- **Distance metric**: Cosine similarity
- **Hybrid indexing**: Dense vectors + sparse vectors (fastembed for BM25)
- **Metadata fields**: ticker, title, link, relevance_score

### 5. Retrieval Factory (`src/rag/retrievers.py`)

Six retriever types available via factory pattern:

| Type | Description | Use Case |
|------|-------------|----------|
| `base` | Simple vector similarity | Quick single-perspective search |
| `self_query` (default) | Natural language → metadata filters | "AAPL news about earnings" |
| `multi_query` | Query expansion (3-5 perspectives) | Complex ambiguous questions |
| `contextual_compression` | LLM-based relevance filtering | High precision requirements |
| `hybrid` | Dense + sparse (BM25) search | Best of semantic + keyword |
| `ensemble` | Combines multiple strategies | Maximum recall |

**Configuration**:
```python
retriever = create_retriever(
    vector_store=vector_store,
    retriever_type="self_query",  # User-selectable
    k=5,                          # Top K results
    score_threshold=0.7,          # Minimum relevance
    ticker_filter=["AAPL", "MSFT"] # Optional filter
)
```

### 6. RAG Chain (`src/rag/chain.py`)

**LCEL-only implementation** (NO LangGraph):
```python
chain = (
    RunnableParallel(
        context=retriever | format_docs,
        question=RunnablePassthrough(),
    )
    | RAG_PROMPT
    | llm
    | StrOutputParser()
)
```

**Prompt template**:
- System role: Financial news assistant
- Instructions: Cite sources with [title](link) markdown
- Context injection: Retrieved article chunks
- Output format: Answer + source citations

### 7. Generation
- **Model**: gpt-4o-mini (cost-effective, fast)
- **Temperature**: 0.3 (balanced determinism)
- **Max tokens**: 500
- **Source citation**: Enforced via prompt

## Project Structure

```
pulse/
├── packages/
│   ├── backend/                   # FastAPI application
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── middleware/   # CORS, logging, rate limiting
│   │   │   │   └── routes/       # auth.py, chat.py, health.py
│   │   │   ├── core/             # Security, logging, exceptions, metrics
│   │   │   ├── db/               # SQLAlchemy session, base models
│   │   │   ├── models/           # User, ChatHistory ORM models
│   │   │   ├── rag/              # 6-file RAG pipeline
│   │   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   ├── services/         # Business logic layer
│   │   │   ├── utils/            # Helper functions
│   │   │   ├── config.py         # Environment variable config
│   │   │   └── main.py           # FastAPI app entry point
│   │   ├── tests/
│   │   │   ├── unit/             # 15 test files
│   │   │   ├── integration/      # 3 test files
│   │   │   ├── e2e/              # 1 test file
│   │   │   └── llm_evaluation/   # 8 DeepEval metrics
│   │   ├── scripts/
│   │   │   ├── ingest_data.py    # Vector DB ingestion script
│   │   │   └── check_and_ingest.py # Conditional ingestion (for Docker)
│   │   ├── data/
│   │   │   └── stock_news.json   # 138 news articles (7 tickers, 585KB)
│   │   ├── alembic/              # Database migrations
│   │   ├── pyproject.toml        # uv dependencies
│   │   ├── Dockerfile            # Production image
│   │   └── docker-entrypoint.sh  # Migration verification
│   └── frontend/                 # Next.js application
│       ├── src/
│       │   ├── app/              # App Router pages
│       │   ├── components/
│       │   │   ├── auth/         # Login, register, protected route
│       │   │   ├── chat/         # 10 chat components
│       │   │   ├── layout/       # Header, footer
│       │   │   └── ui/           # 14 shadcn components
│       │   ├── hooks/            # useAuth, useChat, useTickers
│       │   ├── stores/           # Zustand: chat, auth, RAG settings
│       │   ├── lib/              # API client, auth utilities
│       │   ├── types/            # TypeScript interfaces
│       │   ├── schemas/          # Zod validation
│       │   └── middleware.ts     # Auth middleware
│       ├── tests/
│       │   ├── unit/components/  # 10 Vitest component tests
│       │   └── e2e/              # 2 Playwright specs
│       ├── package.json
│       ├── next.config.js        # Next.js configuration
│       └── Dockerfile            # Production image
└── docker/
    ├── docker-compose.yml        # Development services
    └── docker-compose.prod.yml   # Production stack
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_username ON users(username);
```

### Chat History Table
```sql
CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    sources JSONB,                -- Array of source objects
    metadata JSONB,               -- Retriever config, timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at DESC);
```

**Note**: Python model uses `metadata_` (underscore) to avoid SQLAlchemy reserved word conflict.

## Production Infrastructure

### Docker Entrypoint Migration Verification

The `docker-entrypoint.sh` script includes critical safety checks:

```bash
#!/bin/bash
set -e

# Run database migrations
uv run alembic upgrade head

# Verify migrations created expected tables
verify_migrations() {
    uv run python -c "
    # Check for users and chat_history tables
    # Check alembic_version has entry
    # Exit 1 if verification fails
    "
}

verify_migrations || {
    echo "ERROR: Migration verification failed"
    exit 1
}

# Only start server if database schema is valid
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Why this matters**: Prevents known issue where Alembic reports success but tables aren't created.

### Observability Stack

1. **Sentry** (`src/core/sentry.py`)
   - Error tracking and performance monitoring
   - Environment: production/staging/development
   - Sample rate: 1.0 (100% for production)
   - Integrations: FastAPI, SQLAlchemy, Redis

2. **LangSmith** (`src/rag/tracing.py`)
   - LLM call tracing and evaluation
   - Trace RAG chain execution
   - Monitor retrieval quality
   - Debug prompt engineering

3. **Prometheus Metrics** (`src/core/metrics.py`)
   - Request latency histograms
   - Error rate counters
   - Active user gauge
   - Vector search performance

### Security Features

1. **Authentication**
   - JWT tokens with 60-minute expiration
   - Bcrypt password hashing (12 rounds)
   - HTTPOnly cookies (production)
   - CSRF protection

2. **Rate Limiting**
   - SlowAPI integration
   - 10 requests/minute per user (chat endpoint)
   - 5 requests/minute (auth endpoints)
   - Redis-backed storage

3. **CORS**
   - Whitelist origins only
   - Credentials allowed
   - Preflight caching

4. **Docker Security**
   - Non-root user (appuser)
   - Read-only data mounts
   - No privileged containers
   - Minimal base images (Alpine)

## Testing Architecture

**Total: 39 test files across 5 layers**

### Backend Tests (27 files)

**Unit (15 tests)** - `tests/unit/`
- test_chain.py
- test_config.py
- test_data_loader.py
- test_database.py
- test_db_session.py
- test_embeddings.py
- test_exceptions.py
- test_logging.py
- test_models.py
- test_retrievers.py
- test_schemas.py
- test_security.py
- test_services.py
- test_utils.py
- test_vector_store.py

**Integration (3 tests)** - `tests/integration/`
- test_auth_routes.py
- test_chat_routes.py
- test_db.py

**E2E (1 test)** - `tests/e2e/`
- test_full_flow.py

**LLM Evaluation (8 tests)** - `tests/llm_evaluation/`
- test_answer_relevancy.py
- test_bias.py
- test_context_precision.py
- test_context_recall.py
- test_faithfulness.py
- test_hallucination.py
- test_link_accuracy.py
- test_source_citation.py

### Frontend Tests (12 files)

**Unit (10 tests)** - `tests/unit/components/`
- ChatContainer.test.tsx
- ChatInput.test.tsx
- ChatMessage.test.tsx
- GroupedSourcesList.test.tsx
- LoginForm.test.tsx
- RAGSettings.test.tsx
- RegisterForm.test.tsx
- SourceCard.test.tsx
- SourcesList.test.tsx
- TickerFilter.test.tsx

**E2E (2 tests)** - `tests/e2e/`
- auth.spec.ts (5 test cases)
- chat.spec.ts (5 test cases)

**Mocking Strategy**:
- Unit tests: `vi.fn()` for isolated testing
- E2E tests: Real API calls (no MSW)
- Integration tests: testcontainers for databases

## Performance Characteristics

| Metric | Target | Actual |
|--------|--------|--------|
| API Response (p95) | < 2s | ~1.2s |
| Vector Search | < 500ms | ~300ms |
| Embedding Generation | < 800ms | ~600ms |
| LLM Generation | < 1s | ~800ms |
| Database Query | < 50ms | ~20ms |

## Deployment

### Development
```bash
make dev  # Starts all services locally
```

### Production
```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

**Requirements**:
- Docker 20.0+
- 4GB RAM minimum
- 10GB disk space
- OpenAI API key

## Technology Choices Rationale

### Why LCEL over LangGraph?
- **Simplicity**: Straightforward RAG pipeline, no multi-agent coordination
- **Performance**: Lower overhead for single-chain execution
- **Maintainability**: Easier to debug and modify
- **Composability**: Pipe operator provides clean chain composition

### Why Qdrant?
- **Metadata filtering**: Superior ticker-based filtering
- **Hybrid search**: Built-in dense + sparse vector support
- **Performance**: Fast similarity search with HNSW indexing
- **Self-hosted**: Docker deployment for data privacy

### Why uv?
- **Speed**: 10-100x faster than pip
- **Lock file**: uv.lock ensures reproducible builds
- **Compatibility**: Drop-in pip replacement
- **Virtual env**: Built-in venv management

### Why Zustand v5?
- **Simplicity**: Minimal boilerplate vs Redux
- **Performance**: No unnecessary re-renders
- **Persistence**: Built-in localStorage middleware
- **TypeScript**: Excellent type inference
