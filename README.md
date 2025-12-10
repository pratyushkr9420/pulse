# Pulse - Stock News Chatbot 📈

> An AI-powered chatbot that answers your questions about tech stocks using real financial news articles.

**Ask questions like:**
- "What's the latest news about Apple?"
- "Compare MSFT and AAPL performance"
- "Show me NVDA earnings news"

Every answer includes **clickable links** to source articles for verification.

---

## 🎯 What is Pulse?

Pulse is a **RAG (Retrieval-Augmented Generation)** chatbot that:
1. Searches through 138 financial news articles about 7 tech stocks
2. Finds the most relevant articles for your question
3. Uses AI to generate a natural language answer
4. Provides source citations so you can verify the information

**Supported Stock Tickers**: AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM

---

## ✨ Key Features

- 🤖 **Natural Language Queries**: Ask questions in plain English
- 📚 **Source Citations**: Every answer includes links to source articles with relevance scores
- 🎯 **Ticker Filtering**: Filter responses by specific stock symbols
- 💬 **Chat History**: Your conversations are saved and persistent
- 🔐 **User Authentication**: Secure JWT-based login system
- 📊 **Multiple Retrieval Strategies**: Choose from 6 different retrieval methods
- 🎨 **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS

---

## 🛠 Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router, React 19)
- **Language**: TypeScript 5.7
- **State Management**: Zustand 5 + TanStack Query 5
- **UI Library**: Tailwind CSS + shadcn/ui
- **Forms**: React Hook Form + Zod validation
- **Testing**: Vitest (unit) + Playwright (E2E)

### Backend
- **Framework**: FastAPI (Python 3.12)
- **RAG Framework**: LangChain 0.3.x (LCEL only, NO LangGraph)
- **LLM**: OpenAI gpt-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Vector Database**: Qdrant (with hybrid search: dense + sparse)
- **Relational Database**: PostgreSQL 16
- **Caching**: Redis 7
- **Authentication**: JWT (python-jose + passlib)
- **Package Manager**: uv (10-100x faster than pip)
- **Testing**: pytest + DeepEval (LLM evaluation)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Observability**: Sentry, LangSmith, Prometheus
- **CI/CD**: GitHub Actions

---

## 📋 Prerequisites

Before you begin, you need to have these installed on your computer:

### Required Software

1. **Docker Desktop** (for running databases)
   - Download: https://www.docker.com/products/docker-desktop
   - Why: Runs PostgreSQL, Redis, and Qdrant in containers
   - Verify: `docker --version` (should show version 20.0 or later)

2. **Node.js** (for frontend)
   - Download: https://nodejs.org (get the LTS version)
   - Why: Runs the Next.js frontend application
   - Verify: `node --version` (should show v20.0 or later)

3. **Python 3.12** (for backend)
   - Download: https://www.python.org/downloads/
   - Why: Runs the FastAPI backend application
   - Verify: `python3 --version` (should show 3.12 or later)

4. **uv** (Python package manager)
   - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Why: Fast Python dependency management (replaces pip)
   - Verify: `uv --version`

5. **Make** (build automation)
   - macOS/Linux: Pre-installed
   - Windows: Install via `choco install make` or use Git Bash
   - Why: Simplifies running common commands
   - Verify: `make --version`

### Required API Keys

6. **OpenAI API Key** (REQUIRED)
   - Sign up: https://platform.openai.com/signup
   - Create key: https://platform.openai.com/api-keys
   - Cost: ~$0.01-0.05 per session (very affordable)
   - Why: Powers the AI responses and embeddings

### Optional Services

7. **Sentry** (Optional - Error tracking)
   - Sign up: https://sentry.io
   - Free tier available

8. **LangSmith** (Optional - LLM tracing)
   - Sign up: https://smith.langchain.com
   - Free tier available

---

## 🚀 Quick Start (5 Minutes)

Follow these steps to get Pulse running on your computer:

### Step 1: Get the Code

```bash
# Download the code (if you haven't already)
git clone <repository-url>
cd pulse
```

### Step 2: Configure Environment Variables

#### Backend Configuration

```bash
# Go to the backend directory
cd packages/backend

# Create environment file from template
cp .env.example .env

# Edit the .env file
nano .env  # or use any text editor
```

**In the `.env` file, update these REQUIRED fields:**
```bash
# Replace with your actual OpenAI API key (starts with sk-)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Generate a secure secret (copy the output of this command)
# Run in terminal: openssl rand -hex 32
JWT_SECRET_KEY=paste-the-generated-secret-here
```

**The other fields have sensible defaults and can be left as-is.**

#### Frontend Configuration (Optional)

```bash
# Go to the frontend directory
cd ../frontend

# Create environment file (optional - has defaults)
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Pulse
EOF
```

### Step 3: Start Infrastructure Services

```bash
# Go back to the pulse root directory
cd ../..

# Start PostgreSQL, Redis, and Qdrant using Docker
make docker-up

# Wait ~30 seconds for services to be ready
# You should see: "pulse-postgres", "pulse-redis", "pulse-qdrant" running
```

**Verify services are running:**
```bash
docker ps
# You should see 3 containers running (postgres, redis, qdrant)
```

### Step 4: Set Up the Database

```bash
# Install backend dependencies
cd packages/backend
uv venv          # Create virtual environment
uv sync          # Install dependencies (takes ~1 minute)

# Run database migrations (creates users and chat_history tables)
uv run alembic upgrade head

# Expected output: "Running upgrade -> 257beb0ad1c7, Initial migration..."
```

**Verify the database:**
```bash
# Check that tables were created
docker exec -it pulse-postgres psql -U stocknews -d stocknews -c "\dt"

# You should see:
#  users
#  chat_history
#  alembic_version
```

### Step 5: Ingest News Data

This step loads 138 news articles into the vector database:

```bash
# Still in packages/backend
uv run python scripts/ingest_data.py

# Expected output:
# "Loading documents from JSON..."
# "Documents loaded count=138"
# "Documents chunked chunks=XXX"
# "✅ Data ingestion complete"
```

**This takes 2-5 minutes** (depending on OpenAI API speed). It only needs to be done once.

### Step 6: Start the Backend

```bash
# Start the FastAPI backend server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
# "INFO: Uvicorn running on http://0.0.0.0:8000"
# "INFO: Application startup complete"
```

**Leave this terminal running and open a new terminal for the next step.**

### Step 7: Start the Frontend

```bash
# In a new terminal, go to the frontend directory
cd pulse/packages/frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev

# You should see:
# "▲ Next.js 15.x.x"
# "Local: http://localhost:3000"
```

### Step 8: Use Pulse! 🎉

1. **Open your browser** and go to: http://localhost:3000

2. **Register a new account:**
   - Click "Register"
   - Choose a username (3+ characters)
   - Create a password (8+ characters)
   - Click "Create Account"

3. **Start chatting:**
   - You'll be automatically logged in and taken to the chat page
   - Type a question like: "What's the latest AAPL news?"
   - Click "Send" and wait for the AI response (takes 3-5 seconds)
   - Click on source links to read the original articles

---

## 📖 Detailed Setup Guide

### Understanding the Project Structure

```
pulse/
├── packages/
│   ├── backend/                 # FastAPI application
│   │   ├── src/                 # Source code
│   │   │   ├── api/            # API routes and middleware
│   │   │   ├── core/           # Security, config, logging
│   │   │   ├── models/         # Database models (SQLAlchemy)
│   │   │   ├── schemas/        # Request/response schemas (Pydantic)
│   │   │   ├── services/       # Business logic
│   │   │   ├── rag/            # RAG pipeline (embeddings, retrieval, chain)
│   │   │   └── main.py         # FastAPI app entry point
│   │   ├── tests/              # Test suite
│   │   │   ├── unit/           # Unit tests (15 files)
│   │   │   ├── integration/    # Integration tests (3 files)
│   │   │   ├── e2e/            # End-to-end tests (1 file)
│   │   │   └── llm_evaluation/ # LLM quality tests (8 files)
│   │   ├── scripts/            # Utility scripts
│   │   │   └── ingest_data.py  # Loads news data into Qdrant
│   │   ├── alembic/            # Database migrations
│   │   ├── pyproject.toml      # Python dependencies
│   │   └── Dockerfile          # Production container image
│   │
│   └── frontend/               # Next.js application
│       ├── src/
│       │   ├── app/            # Next.js App Router pages
│       │   ├── components/     # React components
│       │   │   ├── chat/       # Chat UI components (10 files)
│       │   │   ├── auth/       # Auth UI components
│       │   │   └── ui/         # shadcn/ui components (14 files)
│       │   ├── hooks/          # Custom React hooks
│       │   ├── stores/         # Zustand state management
│       │   ├── lib/            # Utilities and API client
│       │   └── types/          # TypeScript type definitions
│       ├── tests/              # Test suite
│       │   ├── unit/           # Component tests (10 files)
│       │   └── e2e/            # Playwright E2E tests (2 files)
│       ├── package.json        # Node.js dependencies
│       └── Dockerfile          # Production container image
│
├── docker/
│   ├── docker-compose.yml      # Development infrastructure
│   └── docker-compose.prod.yml # Production stack
│
├── docs/                       # Documentation
│   ├── architecture.md         # System architecture
│   ├── api-spec.md            # API documentation
│   └── testing-strategy.md    # Testing guide
│
├── Makefile                    # Common commands
└── README.md                   # This file
```

### Environment Variables Explained

#### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ YES | Your OpenAI API key | `sk-proj-abc123...` |
| `JWT_SECRET_KEY` | ✅ YES | Secret for JWT tokens | Generate with `openssl rand -hex 32` |
| `DATABASE_URL` | ❌ No | PostgreSQL connection string | Default: `postgresql+asyncpg://stocknews:stocknews@localhost:5432/stocknews` |
| `QDRANT_HOST` | ❌ No | Qdrant server host | Default: `localhost` |
| `QDRANT_PORT` | ❌ No | Qdrant server port | Default: `6333` |
| `REDIS_URL` | ❌ No | Redis connection string | Default: `redis://localhost:6379/0` |
| `ENVIRONMENT` | ❌ No | Environment name | Default: `development` |
| `DEBUG` | ❌ No | Enable debug mode | Default: `false` |
| `SENTRY_DSN` | ❌ No | Sentry error tracking | Leave empty to disable |
| `LANGSMITH_API_KEY` | ❌ No | LangSmith LLM tracing | Leave empty to disable |

**Full reference**: See `packages/backend/.env.example` for all 20+ variables with descriptions.

### Running Individual Services

If you want to run services separately instead of using `make` commands:

#### Start Infrastructure Only
```bash
docker-compose -f docker/docker-compose.yml up -d
```

#### Start Backend Only
```bash
cd packages/backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Only
```bash
cd packages/frontend
npm run dev
```

---

## 🧪 Running Tests

Pulse has 39 test files covering all layers of the application.

### Backend Tests

```bash
cd packages/backend

# Run all unit tests
uv run pytest tests/unit -v

# Run with coverage report
uv run pytest tests/unit --cov=src --cov-report=html

# Run integration tests (requires Docker services)
uv run pytest tests/integration -v

# Run E2E tests
uv run pytest tests/e2e -v

# Run LLM evaluation tests (requires OpenAI API key)
uv run pytest tests/llm_evaluation -v

# Run all tests
uv run pytest -v
```

### Frontend Tests

```bash
cd packages/frontend

# Run unit tests
npm run test:unit

# Run unit tests with coverage
npm run test:unit -- --coverage

# Run E2E tests (requires backend running)
npm run test:e2e

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

### Run All Tests (via Makefile)

```bash
# From the pulse root directory

# Unit + integration tests
make test

# E2E tests
make test-e2e

# LLM evaluation tests
make test-llm

# Coverage reports
make coverage

# Linting and type checking
make lint
make type-check
```

**Test Coverage**: The project maintains 80%+ code coverage across both frontend and backend.

---

## 🛠 Common Commands (Makefile)

The Makefile provides convenient shortcuts for common tasks:

### Development

| Command | Description |
|---------|-------------|
| `make docker-up` | Start infrastructure services (Postgres, Redis, Qdrant) |
| `make docker-down` | Stop infrastructure services |
| `make dev-backend` | Start backend in development mode |
| `make dev-frontend` | Start frontend in development mode |

### Database

| Command | Description |
|---------|-------------|
| `make db-migrate` | Run database migrations (creates tables) |
| `make db-reset` | Reset database (⚠️ destroys all data) |
| `make ingest` | Load news data into Qdrant vector store |

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run unit + integration tests |
| `make test-e2e` | Run end-to-end tests |
| `make test-llm` | Run LLM evaluation tests |
| `make coverage` | Generate coverage reports |

### Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Check code style (frontend + backend) |
| `make lint-fix` | Fix code style issues automatically |
| `make type-check` | Run TypeScript and mypy type checking |

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Remove build artifacts and caches |
| `make clean-docker` | Stop services and remove volumes (⚠️ destroys all data) |

---

## 🚢 Production Deployment

### Option 1: Automated Deployment (Recommended for Quick Start)

The fastest way to deploy Pulse to production is using the automated deployment script:

#### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

#### Quick Deployment

```bash
# 1. Copy and configure environment file
cp docker/.env.prod.example docker/.env.prod

# 2. Edit docker/.env.prod with your production values
# Required:
#   OPENAI_API_KEY=sk-your-production-key
#   JWT_SECRET_KEY=$(openssl rand -hex 32)
#
# Important (review defaults):
#   NEXT_PUBLIC_API_URL=http://localhost:8000  # Change if accessing externally
#   ENABLE_METRICS=true                         # For Prometheus metrics
#   CORS_ORIGINS=http://localhost:3000         # Update to match frontend URL
#
# See docker/.env.prod.example for all 25+ configuration options

# 3. Run automated deployment script
./deploy-prod.sh --build
```

The script will:
- ✅ Validate prerequisites (Docker, Docker Compose)
- ✅ Check environment configuration
- ✅ Build Docker images
- ✅ Start all services (frontend, backend, postgres, redis, qdrant)
- ✅ Wait for services to be healthy
- ✅ Automatically run database migrations (creates tables)
- ✅ Automatically ingest data if vector database is empty
- ✅ Display deployment summary with URLs

**Application will be available immediately at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### Deployment Script Options

```bash
./deploy-prod.sh           # Start all services
./deploy-prod.sh --build   # Force rebuild images
./deploy-prod.sh --logs    # Show logs after deployment
./deploy-prod.sh --down    # Stop and remove all containers
./deploy-prod.sh --help    # Show all options
```

#### Managing the Deployment

```bash
# View logs
docker-compose -f docker/docker-compose.prod.yml logs -f

# Stop services
./deploy-prod.sh --down

# Restart services
./deploy-prod.sh
```

---

### Option 2: Manual Docker Compose Deployment

#### Step 1: Prepare Environment File

```bash
cd docker

# Option 1: Copy from example (RECOMMENDED)
cp .env.prod.example .env.prod
# Then edit .env.prod with your production values

# Option 2: Create minimal .env.prod manually
cat > .env.prod << EOF
# REQUIRED
OPENAI_API_KEY=sk-your-production-key
JWT_SECRET_KEY=$(openssl rand -hex 32)

# IMPORTANT (defaults provided, review for your deployment)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Update for external access
ENABLE_METRICS=true                         # Prometheus metrics
CORS_ORIGINS=http://localhost:3000         # Update to match frontend URL

# OPTIONAL OBSERVABILITY
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LANGSMITH_API_KEY=lsv2_pt_your-key
LANGSMITH_PROJECT=pulse-prod
EOF

# See .env.prod.example for complete list of 25+ variables
```

#### Step 2: Start Production Stack

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Wait for services to be healthy (~1 minute)
docker-compose -f docker-compose.prod.yml ps
```

#### Step 3: Verify Deployment

**Note:** Database migrations and data ingestion are **automated** via docker-entrypoint.sh. When the backend container starts, it will:
1. Run `alembic upgrade head` (creates users and chat_history tables)
2. Verify database schema is correct
3. Check if Qdrant collection has data and ingest if needed

```bash
# Check backend logs (should show "Running database migrations..." and "Database schema verified")
docker-compose -f docker-compose.prod.yml logs backend

# Expected log output includes:
# "Running database migrations..."
# "✓ Database schema verified: users and chat_history tables exist"
# "✓ Migration version: <version>"
# "✅ Collection already has data - skipping ingestion" (or)
# "📥 Collection is empty - starting data ingestion..."
# "✅ Data ingestion complete"

# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"ok","timestamp":"..."}

# Test frontend
curl http://localhost:3000
# Expected: HTML response
```

#### Step 4: Manual Data Re-ingestion (Optional)

**Note:** Data ingestion is **automated** on first startup. This step is only needed if you update the data file.

To manually re-ingest data (if you update `packages/backend/data/stock_news.json`):

```bash
# Manual data ingestion
docker-compose -f docker-compose.prod.yml exec backend \
  uv run python scripts/ingest_data.py

# Expected output: "✅ Data ingestion complete"
```

#### Step 5: Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### Production Checklist

Before deploying to production, ensure:

**Required Configuration:**
- [ ] `OPENAI_API_KEY` is set with a production key
- [ ] `JWT_SECRET_KEY` is generated securely (32+ bytes using `openssl rand -hex 32`)

**Important Configuration (review defaults):**
- [ ] `NEXT_PUBLIC_API_URL` is set correctly (use external URL if accessing remotely)
- [ ] `CORS_ORIGINS` includes your frontend domain/URL
- [ ] `ENABLE_METRICS` is set to `true` for Prometheus monitoring

**Security & Environment:**
- [ ] `ENVIRONMENT` is set to `production`
- [ ] `DEBUG` is set to `false`
- [ ] Database password changed from default (in `DATABASE_URL` and docker-compose.prod.yml)

**Observability (recommended):**
- [ ] Sentry DSN is configured for error tracking
- [ ] LangSmith API key is set for LLM observability
- [ ] Prometheus is configured to scrape `/metrics` endpoint

**Operations:**
- [ ] Database volumes are backed up regularly
- [ ] SSL/TLS is configured (via reverse proxy like nginx or Caddy)
- [ ] Rate limiting is enabled (via Redis - enabled by default)

---

## 📊 API Documentation

### Base URL
- Development: `http://localhost:8000`
- API Prefix: `/api/v1`

### Authentication

All chat endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

Get a token by registering and logging in through the frontend, or via API:

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### Interactive API Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly in the browser!

### Key Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/metrics` | GET | No | Prometheus metrics |
| `/api/v1/auth/register` | POST | No | Register user |
| `/api/v1/auth/login` | POST | No | Login (get JWT) |
| `/api/v1/auth/me` | GET | Yes | Current user info |
| `/api/v1/chat` | POST | Yes | Send chat message |
| `/api/v1/chat/history` | GET | Yes | Get chat history |
| `/api/v1/chat/tickers` | GET | No | Available stock tickers |

**Full API documentation**: See `docs/api-spec.md`

---

## 🐛 Troubleshooting

### Common Issues

#### "Docker daemon is not running"
**Problem**: Docker Desktop is not started.
**Solution**:
1. Open Docker Desktop application
2. Wait for it to start (green light in menu bar/tray)
3. Try command again

#### "Port 5432 already in use"
**Problem**: Another PostgreSQL instance is running.
**Solution**:
```bash
# Stop other PostgreSQL instances
# macOS/Linux:
sudo service postgresql stop

# Or use different ports in .env:
# DATABASE_URL=postgresql+asyncpg://stocknews:stocknews@localhost:5433/stocknews
```

#### "ModuleNotFoundError" in backend
**Problem**: Dependencies not installed or wrong Python version.
**Solution**:
```bash
cd packages/backend
python3 --version  # Should be 3.12+
uv venv            # Recreate virtual environment
uv sync            # Reinstall dependencies
```

#### "OPENAI_API_KEY not set"
**Problem**: Environment variable not configured.
**Solution**:
1. Check `packages/backend/.env` file exists
2. Verify `OPENAI_API_KEY=sk-...` is set
3. Restart the backend server

#### "Failed to ingest data"
**Problem**: Qdrant connection issue or OpenAI API error.
**Solution**:
```bash
# Check Qdrant is running
curl http://localhost:6333/health

# Check logs
docker logs pulse-qdrant

# Verify OpenAI API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### Frontend shows "Failed to fetch"
**Problem**: Backend is not running or CORS issue.
**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
3. Check browser console for specific error messages

#### "Alembic migration failed"
**Problem**: Database connection issue or tables already exist.
**Solution**:

For **local development**:
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Reset database (⚠️ destroys data)
cd packages/backend
uv run alembic downgrade base
uv run alembic upgrade head

# Or use Makefile
make db-reset
```

For **production Docker deployment**:
```bash
# Check backend container logs for migration errors
docker-compose -f docker/docker-compose.prod.yml logs backend

# Migrations run automatically via docker-entrypoint.sh
# If migration fails, the container will exit with an error
# To manually run migrations in production:
docker-compose -f docker/docker-compose.prod.yml exec backend \
  uv run alembic upgrade head
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**:
   ```bash
   # Backend logs
   docker-compose logs backend

   # Frontend logs
   # Check the terminal where npm run dev is running

   # Docker service logs
   docker-compose logs postgres
   docker-compose logs qdrant
   docker-compose logs redis
   ```

2. **Verify services are healthy**:
   ```bash
   docker-compose ps
   # All services should show "Up" and "healthy"
   ```

3. **Check the documentation**:
   - `docs/architecture.md` - System architecture
   - `docs/api-spec.md` - API reference
   - `docs/testing-strategy.md` - Testing guide

4. **Open an issue**: Provide error messages, logs, and steps to reproduce.

---

## 🏗 Architecture Overview

### RAG Pipeline

Pulse uses a Retrieval-Augmented Generation (RAG) approach:

1. **User asks a question** → "What's the latest AAPL news?"

2. **Query goes to Retriever** → Searches vector database for relevant articles

3. **Relevant articles retrieved** → Top 5 most similar articles found

4. **Context + Question sent to LLM** → OpenAI gpt-4o-mini generates answer

5. **Response with sources returned** → User sees answer + clickable source links

### Data Flow

```
Frontend (Next.js)
    ↓ HTTP Request
Backend (FastAPI)
    ↓ JWT Validation
Chat Service
    ↓ Question
Retriever (Qdrant)
    ↓ Relevant Docs
LLM (OpenAI)
    ↓ Generated Answer
Response (with sources)
```

### 6 Retriever Types

Pulse supports different retrieval strategies:

1. **self_query** (Default): Automatically extracts filters from natural language
2. **base**: Simple vector similarity search
3. **multi_query**: Generates multiple query variations
4. **contextual_compression**: Uses LLM to compress context
5. **hybrid**: Combines dense and sparse (BM25) search
6. **ensemble**: Combines multiple retriever strategies

You can select these in the UI via "RAG Settings" or via API (`retriever_type` parameter).

---

## 📚 Additional Resources

### Documentation Files

- **`docs/architecture.md`**: Detailed system architecture and design decisions
- **`docs/api-spec.md`**: Complete API reference with examples
- **`docs/testing-strategy.md`**: Testing pyramid and coverage strategy

### Key Technologies

- **LangChain**: https://python.langchain.com/docs/get_started/introduction
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **Qdrant**: https://qdrant.tech/documentation/
- **OpenAI**: https://platform.openai.com/docs/

### Project Specifications

- **Implementation Guide**: `../implementation/IMPLEMENTATION_GUIDE.md` (12,000+ lines)
- **Tech Stack Reference**: `../project_docs/tech_stack_quick_reference.md`
- **Project Rules**: `../project_docs/.cursorrules` (1,925 lines)

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 🙋 FAQ

**Q: How much does it cost to run Pulse?**
A: The main cost is OpenAI API usage (~$0.01-0.05 per session). All other components are free and open-source.

**Q: Can I use a different LLM instead of OpenAI?**
A: Yes! You can modify `src/rag/chain.py` to use any LangChain-compatible LLM (Anthropic Claude, local models via Ollama, etc.).

**Q: How do I add more news articles?**
A: Add articles to `packages/backend/data/stock_news.json` following the existing format, then run `make ingest` to reindex.

**Q: Can I deploy this to AWS/GCP/Azure?**
A: Yes! The Docker Compose setup can be adapted to any cloud provider. You'll need to provision managed PostgreSQL, Redis, and either host Qdrant yourself or use Qdrant Cloud.

**Q: Is this production-ready?**
A: Yes! The codebase includes: proper error handling, health checks, observability (Sentry/LangSmith/Prometheus), migrations, comprehensive testing (39 test files), and production Docker configurations.

**Q: Why NO LangGraph?**
A: LangGraph is for complex multi-agent workflows with state management. Pulse is a straightforward RAG application that doesn't need that complexity. LCEL (LangChain Expression Language) provides clean, composable chains that are easier to understand and maintain.

---

## 🎓 Learning Resources

**New to RAG?**
- Watch: "What is RAG?" - https://www.youtube.com/watch?v=T-D1OfcDW1M
- Read: LangChain RAG Tutorial - https://python.langchain.com/docs/tutorials/rag/

**New to Docker?**
- Docker Get Started: https://docs.docker.com/get-started/

**New to Next.js?**
- Next.js Tutorial: https://nextjs.org/learn

**New to FastAPI?**
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/

---

**Happy querying! 📈🤖**

If you find issues or have questions, please open an issue on GitHub.
