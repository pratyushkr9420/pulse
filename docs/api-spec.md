# Pulse API Specification

## Base URL
`/api/v1`

## Authentication
JWT Bearer tokens. Include in Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Health Check
```
GET /health
```
**Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-02-19T10:30:00Z"
}
```

### Authentication

#### Register
```
POST /auth/register
```
**Request Body**:
```json
{
  "username": "string (3-50 chars)",
  "password": "string (8+ chars)"
}
```
**Response** (201 Created):
```json
{
  "id": "uuid",
  "username": "string",
  "created_at": "datetime"
}
```

#### Login
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```
**Request Body**:
```
username=<username>&password=<password>
```
**Response**:
```json
{
  "access_token": "string (JWT)",
  "token_type": "bearer"
}
```

#### Get Current User
```
GET /auth/me
Authorization: Bearer <token>
```
**Response**:
```json
{
  "id": "uuid",
  "username": "string"
}
```

### Chat

#### Send Message
```
POST /chat
Authorization: Bearer <token>
```
**Request Body**:
```json
{
  "message": "string",
  "ticker_filter": ["AAPL", "MSFT"],
  "retriever_type": "self_query",
  "use_advanced_rag": false
}
```
**Response**:
```json
{
  "id": "uuid",
  "message": "string",
  "response": "string",
  "sources": [
    {
      "title": "Article headline",
      "ticker": "AAPL",
      "link": "https://...",
      "snippet": "Relevant excerpt...",
      "relevance_score": 0.92
    }
  ],
  "created_at": "datetime"
}
```

#### Get History
```
GET /chat/history?limit=50&offset=0
Authorization: Bearer <token>
```
**Response**:
```json
{
  "items": [ChatMessage],
  "total": 100
}
```

### Tickers
```
GET /tickers
```
**Response**:
```json
["AAPL", "MSFT", "AMZN", "NFLX", "NVDA", "INTC", "IBM"]
```

## Error Responses
```json
{
  "detail": "Error message"
}
```

## Status Codes
- 200: Success
- 201: Created (registration)
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error
