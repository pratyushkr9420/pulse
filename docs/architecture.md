# Pulse Architecture

## Overview

Pulse is a RAG-based financial news query system that allows users to ask questions about tech stocks (AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM) and receive answers with cited sources.

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Frontend      │────▶│   Backend       │────▶│   Services      │
│   (Next.js 15)  │     │   (FastAPI)     │     │   (External)    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ - React Query   │     │ - SQLAlchemy    │     │ - OpenAI API    │
│ - Zustand       │     │ - LCEL Chains   │     │ - Qdrant        │
│ - Zod           │     │ - Pydantic      │     │ - PostgreSQL    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
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

## RAG Pipeline

1. **Document Loading**: JSONLoader parses stock_news.json
2. **Text Splitting**: RecursiveCharacterTextSplitter (1000 chunks, 200 overlap)
3. **Embedding**: OpenAI text-embedding-3-small
4. **Storage**: Qdrant with ticker metadata
5. **Retrieval**: SelfQueryRetriever with metadata filtering
6. **Generation**: gpt-4o-mini with citation prompt

## Testing Pyramid

1. **Unit Tests**: Vitest (frontend), pytest (backend)
2. **Integration Tests**: MSW, testcontainers
3. **API Contract Tests**: httpx
4. **E2E Tests**: Playwright
5. **LLM Evaluation**: DeepEval (6 metrics)
