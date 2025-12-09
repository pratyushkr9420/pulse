# Pulse API Specification

## Base URL
```
http://localhost:8000/api/v1
```

**Production**: Replace `localhost:8000` with your deployed backend URL.

## Authentication

Pulse uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid JWT token.

**Include token in Authorization header**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token expiration**: 30 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)

**Protected endpoints**: `/api/v1/chat/*`, `/api/v1/auth/me`

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created (e.g., user registration) |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid JWT token |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request body failed schema validation |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error (check logs) |

## Endpoints

---

### Health Check

Check if the API server is running and healthy.

```http
GET /api/v1/health
```

**Authentication**: None required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-09T10:30:00.123456Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "qdrant": "connected"
  }
}
```

**Example curl**:
```bash
curl http://localhost:8000/api/v1/health
```

---

### Authentication Endpoints

#### Register New User

Create a new user account.

```http
POST /api/v1/auth/register
Content-Type: application/json
```

**Authentication**: None required

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Validation Rules**:
- `username`: 3-50 characters, alphanumeric + underscore, must be unique
- `password`: Minimum 8 characters

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "created_at": "2025-12-09T10:30:00.123456Z"
}
```

**Error Responses**:

*Username already exists* (400 Bad Request):
```json
{
  "detail": "Username already registered"
}
```

*Validation error* (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

**Example curl**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securePassword123"}'
```

---

#### Login

Authenticate and receive JWT access token.

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Authentication**: None required

**Request Body** (form-urlencoded):
```
username=john_doe&password=securePassword123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MzM3MzU0MDB9.signature",
  "token_type": "bearer"
}
```

**Error Responses**:

*Invalid credentials* (401 Unauthorized):
```json
{
  "detail": "Incorrect username or password"
}
```

**Example curl**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securePassword123"
```

**Store the token**: Save `access_token` for subsequent authenticated requests.

---

#### Get Current User

Retrieve authenticated user's profile.

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Authentication**: Required (JWT token)

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "created_at": "2025-12-09T10:30:00.123456Z"
}
```

**Error Responses**:

*Missing token* (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

*Invalid/expired token* (401 Unauthorized):
```json
{
  "detail": "Could not validate credentials"
}
```

**Example curl**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

### Chat Endpoints

#### Send Chat Message

Send a question about stock news and receive an AI-generated response with cited sources.

```http
POST /api/v1/chat
Authorization: Bearer <token>
Content-Type: application/json
```

**Authentication**: Required (JWT token)

**Rate Limit**: 10 requests per minute per user

**Request Body**:
```json
{
  "message": "What is the latest news about Apple's AI initiatives?",
  "retriever_type": "self_query",
  "ticker_filter": ["AAPL"],
  "use_advanced_rag": false
}
```

**Request Parameters**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | Yes | - | User's question (max 2000 chars) |
| `retriever_type` | string | No | `"self_query"` | Retrieval strategy (see below) |
| `ticker_filter` | array | No | `[]` | Filter by tickers (e.g., `["AAPL", "MSFT"]`) |
| `use_advanced_rag` | boolean | No | `false` | Enable advanced RAG (multi-query + compression) |

**Retriever Types**:

| Value | Description | Best For |
|-------|-------------|----------|
| `self_query` | Natural language → metadata filters | Most queries (default) |
| `base` | Simple vector similarity | Quick single-perspective search |
| `multi_query` | Query expansion with 3-5 perspectives | Complex/ambiguous questions |
| `contextual_compression` | LLM-based relevance filtering | High precision requirements |
| `hybrid` | Dense + sparse (BM25) search | Best of semantic + keyword |
| `ensemble` | Combines multiple strategies | Maximum recall |

**Response** (200 OK):
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "What is the latest news about Apple's AI initiatives?",
  "response": "Apple has been making significant strides in AI, particularly with the integration of AI features into iOS 18. According to recent reports, [Apple is focusing on on-device AI processing](https://example.com/apple-ai-1) to enhance privacy and performance. The company has also [announced partnerships with OpenAI](https://example.com/apple-ai-2) to bring advanced AI capabilities to Siri and other applications.",
  "sources": [
    {
      "title": "Apple Announces Major AI Features in iOS 18",
      "ticker": "AAPL",
      "link": "https://example.com/apple-ai-1",
      "snippet": "Apple is focusing on on-device AI processing to enhance privacy and performance, marking a significant shift in the company's AI strategy...",
      "relevance_score": 0.94
    },
    {
      "title": "Apple Partners with OpenAI for Enhanced Siri",
      "ticker": "AAPL",
      "link": "https://example.com/apple-ai-2",
      "snippet": "In a groundbreaking move, Apple has announced a partnership with OpenAI to bring advanced conversational AI to Siri...",
      "relevance_score": 0.88
    }
  ],
  "metadata": {
    "retriever_type": "self_query",
    "use_advanced_rag": false,
    "ticker_filter": ["AAPL"],
    "retrieved_count": 2
  },
  "created_at": "2025-12-09T10:35:22.456789Z"
}
```

**Error Responses**:

*Unauthorized* (401):
```json
{
  "detail": "Not authenticated"
}
```

*Rate limit exceeded* (429):
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

*Invalid retriever type* (422):
```json
{
  "detail": [
    {
      "loc": ["body", "retriever_type"],
      "msg": "value is not a valid enumeration member; permitted: 'self_query', 'base', 'multi_query', 'contextual_compression', 'hybrid', 'ensemble'",
      "type": "type_error.enum"
    }
  ]
}
```

**Example curl**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the latest news about Apple?",
    "retriever_type": "self_query",
    "ticker_filter": ["AAPL"],
    "use_advanced_rag": false
  }'
```

---

#### Get Chat History

Retrieve user's chat history with pagination.

```http
GET /api/v1/chat/history?limit=50&offset=0
Authorization: Bearer <token>
```

**Authentication**: Required (JWT token)

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `50` | Number of messages to return (max 100) |
| `offset` | integer | No | `0` | Number of messages to skip (pagination) |

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "message": "What is the latest news about Apple?",
      "response": "Apple has been making significant strides...",
      "sources": [
        {
          "title": "Apple Announces Major AI Features",
          "ticker": "AAPL",
          "link": "https://example.com/article",
          "snippet": "Apple is focusing on...",
          "relevance_score": 0.94
        }
      ],
      "metadata": {
        "retriever_type": "self_query",
        "use_advanced_rag": false
      },
      "created_at": "2025-12-09T10:35:22.456789Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "message": "Tell me about Microsoft earnings",
      "response": "According to recent reports...",
      "sources": [...],
      "metadata": {...},
      "created_at": "2025-12-09T09:22:15.123456Z"
    }
  ],
  "total": 127,
  "limit": 50,
  "offset": 0
}
```

**Example curl**:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl "http://localhost:8000/api/v1/chat/history?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### Get Available Tickers

Retrieve list of supported stock tickers.

```http
GET /api/v1/chat/tickers
```

**Authentication**: None required

**Response** (200 OK):
```json
{
  "tickers": ["AAPL", "MSFT", "AMZN", "NFLX", "NVDA", "INTC", "IBM"],
  "count": 7
}
```

**Example curl**:
```bash
curl http://localhost:8000/api/v1/chat/tickers
```

---

## Rate Limiting

Pulse implements rate limiting to prevent abuse:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/chat` | 10 requests | 1 minute |
| `/api/v1/auth/register` | 5 requests | 1 minute |
| `/api/v1/auth/login` | 5 requests | 1 minute |
| All other endpoints | 60 requests | 1 minute |

**Rate limit headers** (included in response):
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1702123456
```

**Exceeded rate limit** (429 Too Many Requests):
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

**Validation errors** (422) include field details:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

---

## Complete API Example Workflow

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "trader123", "password": "securePass456"}'

# Response: {"id": "...", "username": "trader123", "created_at": "..."}

# 2. Login to get JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=trader123&password=securePass456" \
  | jq -r '.access_token')

# 3. Ask a question about stock news
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the latest developments with NVIDIA AI chips?",
    "retriever_type": "hybrid",
    "ticker_filter": ["NVDA"],
    "use_advanced_rag": false
  }'

# 4. View chat history
curl http://localhost:8000/api/v1/chat/history?limit=10 \
  -H "Authorization: Bearer $TOKEN"

# 5. Check API health
curl http://localhost:8000/api/v1/health
```

---

## Schema Definitions

### User Schema
```typescript
{
  id: string (uuid)
  username: string (3-50 chars)
  created_at: string (ISO 8601 datetime)
}
```

### ChatMessage Schema
```typescript
{
  id: string (uuid)
  message: string (max 2000 chars)
  response: string
  sources: SourceInfo[]
  metadata: {
    retriever_type: string
    use_advanced_rag: boolean
    ticker_filter: string[]
    retrieved_count: number
  }
  created_at: string (ISO 8601 datetime)
}
```

### SourceInfo Schema
```typescript
{
  title: string
  ticker: string (one of: AAPL, MSFT, AMZN, NFLX, NVDA, INTC, IBM)
  link: string (URL)
  snippet: string (relevant excerpt, max 500 chars)
  relevance_score: number (0.0-1.0)
}
```
