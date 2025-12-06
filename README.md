# Pulse - Stock News Chatbot

An AI-powered RAG chatbot for querying financial news about tech stocks.

## Features

- **Natural Language Queries**: Ask questions about AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM
- **Source Citations**: Every answer includes clickable links to source articles
- **Ticker Filtering**: Filter responses by specific stock symbols
- **Chat History**: Persistent conversation history per user

## Tech Stack

### Frontend
- Next.js 15 (App Router)
- TypeScript
- TanStack Query + Zustand
- Tailwind CSS + shadcn/ui
- React Hook Form + Zod

### Backend
- FastAPI
- LangChain LCEL (NO LangGraph)
- OpenAI (gpt-4o-mini, text-embedding-3-small)
- Qdrant Vector Store
- PostgreSQL + SQLAlchemy
- JWT Authentication

## Quick Start

```bash
# Start services
make dev

# Initialize database
make db-migrate
make db-seed

# Ingest news data
make ingest

# Run tests
make test
```

## Project Structure

```
pulse/
├── packages/
│   ├── frontend/         # Next.js app
│   └── backend/          # FastAPI app
├── docker/               # Docker configs
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/auth/register` | POST | No | Register user |
| `/auth/login` | POST | No | Login (get JWT) |
| `/auth/me` | GET | Yes | Current user |
| `/chat` | POST | Yes | Send message |
| `/chat/history` | GET | Yes | Get history |
| `/tickers` | GET | No | Available tickers |

## Coverage

- **Target**: 80%
- **Testing Pyramid**: Unit → Integration → API → E2E → LLM Evaluation

## License

MIT
