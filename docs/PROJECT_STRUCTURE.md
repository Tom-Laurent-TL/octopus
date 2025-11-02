# Project Architecture

This document describes the project structure and architectural decisions for the FastAPI application.

## Overview

This application follows a **feature-based architecture** with clear layer separation, making it scalable, maintainable, and easy to understand.

## Directory Structure

```
octopus/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   └── v1/                    # API version 1
│   │       ├── __init__.py
│   │       └── router.py          # Aggregate all feature routers
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration and settings
│   │   ├── security.py           # Authentication and security
│   │   └── bootstrap.py          # System initialization endpoint
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection and session
│   │   └── models.py             # SQLAlchemy models
│   │
│   └── features/                  # Feature modules (domain-driven)
│       ├── __init__.py
│       ├── api_keys/              # API key management feature
│       │   ├── __init__.py
│       │   ├── router.py         # API endpoints
│       │   ├── schemas.py        # Pydantic schemas
│       │   └── service.py        # Business logic layer
│       ├── conversations/         # Chat conversations feature
│       │   ├── __init__.py
│       │   ├── router.py         # API endpoints
│       │   ├── schemas.py        # Pydantic schemas
│       │   └── service.py        # Business logic layer
│       ├── users/                 # User management feature
│       │   ├── __init__.py
│       │   ├── router.py         # API endpoints
│       │   ├── schemas.py        # Pydantic schemas
│       │   └── service.py        # Business logic layer
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Test configuration and fixtures
│   │
│   ├── api/                      # API tests (mirrors app/api)
│   │   └── v1/
│   │       └── test_endpoints.py # API v1 endpoint tests
│   │
│   ├── features/                 # Feature tests (mirrors app/features)
│   │   ├── conversations/
│   │   │   ├── test_router.py   # Router/endpoint tests
│   │   │   └── test_service.py  # Service layer tests
│   │   └── users/
│   │       ├── test_router.py   # Router/endpoint tests
│   │       └── test_service.py  # Service layer tests
│   │
│   └── db/                       # Database tests (mirrors app/db)
│       └── test_models.py        # Model tests
│
├── examples/                      # API usage examples
│   ├── README.md                 # curl command examples & documentation
│   └── demo.py                   # End-to-end demo script (Python)
│
├── docs/                          # Documentation
├── .env                          # Environment variables
├── pyproject.toml                # Project dependencies and config
├── Dockerfile                    # Docker configuration
└── README.md                     # Project overview
```

## Architecture Principles

### 1. Feature-Based Organization
- **Self-contained features**: Each feature is in its own directory with all related code
- **Easy navigation**: Find all code for a feature in one place
- **Scalability**: Add new features without modifying existing ones
- **Clear boundaries**: Each feature owns its routes, schemas, and business logic

### 2. Layered Architecture

#### API Layer (`app/api/`)
- Routes and API versioning
- Aggregates feature routers
- All endpoints prefixed with `/api/v1/`

#### Core Layer (`app/core/`)
- Cross-cutting concerns
- Configuration management (Pydantic settings)
- Security and authentication
- System initialization (bootstrap endpoint)

#### Database Layer (`app/db/`)
- SQLAlchemy models
- Database connection and session management
- Shared database utilities

#### Features Layer (`app/features/`)
- Business logic organized by domain
- Each feature contains:
  - **router.py**: HTTP endpoints (FastAPI routes)
  - **schemas.py**: Data validation (Pydantic models)
  - **service.py**: Business logic and database operations

### 3. Service Layer Pattern

Each feature follows a three-layer pattern:

```
HTTP Request
    ↓
Router (router.py)          # Handle HTTP, call service
    ↓
Service (service.py)        # Business logic, database ops
    ↓
Model (db/models.py)        # Database schema
```

**Benefits:**
- Separation of concerns
- Testable business logic (independent of HTTP)
- Reusable across different interfaces (API, CLI, workers)

### 4. Test Organization

Tests mirror the application structure:
- `tests/api/` → mirrors `app/api/`
- `tests/features/` → mirrors `app/features/`
- `tests/db/` → mirrors `app/db/`

Each feature has two types of tests:
- **test_router.py**: HTTP endpoint behavior
- **test_service.py**: Business logic and database operations

## Current Features

### API Key Management (`app/features/api_keys/`)
Database-backed multi-key system with scope-based access control and enterprise-grade security features.

**Endpoints:**
- `POST /bootstrap` - Create initial master API key (one-time, in `app/core/bootstrap.py`)
- `POST /api/v1/api-keys/` - Create new API key (requires admin scope)
- `GET /api/v1/api-keys/` - List all API keys (requires admin scope)
- `GET /api/v1/api-keys/{key_id}` - Get specific API key details
- `PATCH /api/v1/api-keys/{key_id}` - Update API key (requires admin scope)
- `POST /api/v1/api-keys/{key_id}/deactivate` - Deactivate API key
- `DELETE /api/v1/api-keys/{key_id}` - Delete API key (requires admin scope)
- `POST /api/v1/api-keys/{key_id}/rotate` - Rotate API key (new feature)
- `GET /api/v1/api-keys/{key_id}/audit-logs` - Get audit trail for a key
- `GET /api/v1/api-keys/expiring` - List keys expiring soon
- `POST /api/v1/api-keys/cleanup-expired` - Remove expired keys

**Features:**
- Scope-based access control (read, write, admin)
- Optional expiration dates with automated cleanup
- Usage tracking (last_used_at, last_used_ip)
- Soft delete (is_active flag)
- Secure key generation (cryptographically random)
- Safety checks (can't delete/rotate key you're using)
- Master key in .env for bootstrapping

**Security Features (Production-Ready):**
- **Rate Limiting**: 
  - Global: 100 requests/minute
  - Authentication: 10 requests/minute
  - Key creation: 5 requests/minute
- **Audit Logging**: Complete database trail of all operations
  - Tracks: action, performer, IP address, timestamp, details
  - Accessible via API endpoints
- **Monitoring**: Structured logging for security events
  - WARNING level for failed authentication
  - INFO level for successful operations
  - Includes IP addresses and failure reasons
- **IP Whitelisting**: Restrict keys to specific IPs (IPv4/IPv6)
- **Key Rotation**: Automated workflow for secure key replacement
- **Expiration Management**: Automatic detection and cleanup

See [API Key Security](API_KEY_SECURITY.md) for detailed security documentation.

### Conversations (`app/features/conversations/`)
Manages chat conversations with message history and multi-user participation.

**Endpoints:**
- `POST /api/v1/conversations/` - Create conversation (with participant_ids)
- `GET /api/v1/conversations/` - List all conversations
- `GET /api/v1/conversations/user/{user_id}` - List conversations for a user
- `GET /api/v1/conversations/{id}` - Get conversation with messages
- `PUT /api/v1/conversations/{id}` - Update conversation
- `DELETE /api/v1/conversations/{id}` - Delete conversation
- `POST /api/v1/conversations/{id}/participants` - Add participant
- `DELETE /api/v1/conversations/{id}/participants/{user_id}` - Remove participant
- `POST /api/v1/conversations/{id}/messages` - Add message (with user_id tracking)
- `GET /api/v1/conversations/{id}/messages` - Get messages

**Features:**
- Many-to-many relationships (multiple users per conversation)
- Dynamic participant management
- Message sender tracking (user_id validation)
- Cascade deletion (delete conversation → delete messages)
- Role-based messages (user/assistant/system)
- Pagination support

### Users (`app/features/users/`)
User management with authentication.

**Endpoints:**
- `POST /api/v1/users/` - Register user (public)
- `GET /api/v1/users/` - List users (protected)
- `GET /api/v1/users/{id}` - Get user by ID (protected)
- `GET /api/v1/users/username/{username}` - Get by username (public)
- `PUT /api/v1/users/{id}` - Update user (protected)
- `DELETE /api/v1/users/{id}` - Delete user (protected)

**Features:**
- Password hashing with bcrypt
- Email/username uniqueness validation
- Public vs protected endpoints
- Relationship with conversations

## Authentication

The application uses header-based API key authentication:

**Linux/Mac/WSL (curl):**
```bash
# Protected endpoints require Octopus-API-Key header
curl -H "Octopus-API-Key: your-secret-api-key" http://localhost:8000/api/v1/users/

# Public endpoints don't require authentication
curl http://localhost:8000/api/v1/users/username/john
```

**Windows PowerShell:**
```powershell
# Protected endpoints
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/" -Headers @{"Octopus-API-Key"="your-secret-api-key"} -Method Get

# Public endpoints
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/username/john" -Method Get
```

Configure API key in `.env`:
```env
API_KEY=your-secret-api-key-here
```

## Database

### Models

**APIKey**
- id, key_hash, name, description, scopes, is_active, expires_at, created_at, last_used_at
- **New fields**: last_used_ip (VARCHAR 45), allowed_ips (TEXT, comma-separated)
- Relationships: audit_logs (one-to-many)

**APIKeyAuditLog** (New Model)
- id, api_key_id (FK), action, performed_by, ip_address, details, timestamp
- Relationships: api_key (many-to-one)
- Tracks: create, update, rotate, deactivate, delete, auth_success, auth_failure

**User**
- id, email, username, hashed_password, full_name, is_active, is_superuser
- Relationships: conversations (many-to-many via conversation_participants)

**Conversation**
- id, title, created_at, updated_at
- Relationships: participants (many-to-many with User), messages (one-to-many, cascade delete)

**Message**
- id, content, role, created_at, conversation_id (FK), user_id (FK, nullable)
- Relationships: conversation (many-to-one), user (many-to-one)

**Association Tables**
- conversation_participants: Links users to conversations (many-to-many)

### Relationships
- APIKey → APIKeyAuditLog (one-to-many) - Tracks all operations on a key
- User ↔ Conversations (many-to-many via conversation_participants)
- Conversation → Messages (one-to-many with cascade delete)
- Message → User (many-to-one, optional - tracks who sent the message)
- Message → Conversation (many-to-one)

## Configuration

Environment variables (`.env`):
```env
API_KEY=your-secret-api-key-here
DATABASE_URL=sqlite:///./chat_conversations.db
```

Managed by Pydantic Settings in `app/core/config.py`.

## Adding New Features

1. Create a new directory in `app/features/<feature_name>/`
2. Add `__init__.py`, `router.py`, `schemas.py`, and `service.py`
3. Register the router in `app/api/v1/router.py`
4. Create matching test directory in `tests/features/<feature_name>/`
5. Write tests in `test_router.py` and `test_service.py`

Example structure for a new feature:
```
app/features/products/
├── __init__.py
├── router.py          # HTTP endpoints
├── schemas.py         # Pydantic models for validation
└── service.py         # Business logic and database operations

tests/features/products/
├── __init__.py
├── test_router.py     # Test HTTP endpoints
└── test_service.py    # Test business logic
```
