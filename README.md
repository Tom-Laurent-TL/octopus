# FastAPI App

A production-ready FastAPI application with feature-based architecture, comprehensive testing, and clean separation of concerns.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd octopus

# Install dependencies
uv sync
uv sync --extra test
```

### Configuration

Create a `.env` file in the project root:

```env
MASTER_API_KEY=your-secret-api-key-here
DATABASE_URL=sqlite:///./chat_conversations.db
```

### Run the Application

```bash
# Development server with auto-reload
uv run fastapi dev app/main.py

# Production server
uv run fastapi run app/main.py
```

Navigate to:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Bootstrap (First Time Setup)

On first run, create your master API key by calling the bootstrap endpoint (in `app/core/bootstrap.py`):

**Windows PowerShell:**
```powershell
# Use the provided script
.\scripts\bootstrap.ps1

# Or manually:
Invoke-RestMethod -Uri "http://localhost:8000/bootstrap" -Method Post
```

**Linux/Mac/WSL:**
```bash
curl -X POST http://localhost:8000/bootstrap
```

This will return your master API key. **Save it securely** - add it to your `.env` file:
```env
MASTER_API_KEY=octopus_xyz...your-key-here
```

### Run Tests

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific feature tests
uv run pytest tests/features/users/ -v
```

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Feature Implementation Guide](docs/FEATURE_IMPLEMENTATION_GUIDE.md)** - Step-by-step guide for building new features
- **[Best Practices](docs/BEST_PRACTICES.md)** - Real-world lessons learned and common pitfalls to avoid
- **[Project Architecture](docs/PROJECT_STRUCTURE.md)** - Architecture overview, directory structure, and current features

👉 **New to the project?** Start with the [Documentation Index](docs/README.md)

## 🏗️ Architecture

This application follows a **feature-based architecture** with clear layer separation:

```
app/
├── core/              # Configuration, security, and system initialization
│   ├── config.py      # Application settings
│   ├── security.py    # Authentication verification
│   └── bootstrap.py   # System initialization endpoint
├── db/                # Database models and setup
├── features/          # Feature modules
│   ├── api_keys/      # API key management feature
│   ├── conversations/ # Chat conversation feature
│   └── users/         # User management feature
└── api/v1/            # API version routing
```

### Key Principles

- **Feature-based structure**: Each feature is self-contained
- **Service layer pattern**: Business logic separated from HTTP concerns
- **Comprehensive testing**: Both unit and integration tests
- **Type safety**: Full type hints with Pydantic validation

## 🔑 Features

### Production Features

- **API Key Management** (`/api/v1/api-keys/`)
  - Multiple API keys with custom scopes (read, write, admin)
  - **Rate limiting** - Protection against brute force attacks
  - **Audit logging** - Complete trail of all key operations
  - **Key rotation** - Built-in rotation support
  - **IP whitelisting** - Restrict keys to specific IPs
  - **Expiration management** - Automatic cleanup of expired keys
  - **Monitoring** - Structured logging for security events
  - Usage tracking (last used timestamp and IP)
  - See [API Key Security](docs/API_KEY_SECURITY.md) for details

- **User Management** (`/api/v1/users/`)
  - User registration and authentication
  - Password hashing with bcrypt
  - Public and protected endpoints
  
- **Conversations** (`/api/v1/conversations/`)
  - Create and manage chat conversations
  - Message history with role-based storage
  - Cascade deletion support

### Demo Features

The following features are included as examples from the FastAPI tutorial:

- **Items** (`/api/v1/items/`) - Simple CRUD example
- **Admin** (`/api/v1/admin/`) - Protected endpoint example

> **Note:** Demo features can be removed or replaced with your own features. Study `conversations/` and `users/` for complete implementation patterns.

### Authentication

The application uses a database-backed API key system with scopes for fine-grained access control.

#### Using API Keys

API uses header-based authentication with the `Octopus-API-Key` header:

**Linux/Mac/WSL:**
```bash
curl -H "Octopus-API-Key: your-secret-api-key" http://localhost:8000/api/v1/users/
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/" -Headers @{"Octopus-API-Key"="your-secret-api-key"}

# Or use the included test script
.\scripts\test-api.ps1
```

**Or use the interactive API docs at** http://localhost:8000/docs

#### Managing API Keys

Once you have your master API key, you can create additional keys with specific scopes:

```bash
# Create a new API key with read-only access
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Octopus-API-Key: your-master-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Read-Only Key", "scopes": "read", "description": "For monitoring tools"}'

# List all API keys
curl -H "Octopus-API-Key: your-master-key" http://localhost:8000/api/v1/api-keys/

# Deactivate an API key
curl -X POST "http://localhost:8000/api/v1/api-keys/2/deactivate" \
  -H "Octopus-API-Key: your-master-key"
```

**Available Scopes:**
- `read` - Read-only access to resources
- `write` - Create and update resources
- `admin` - Full access including API key management

**Security Features:**
- Keys are only shown once upon creation
- Track last usage timestamp and IP address for each key
- Set optional expiration dates with automated cleanup
- Deactivate keys without deletion (audit trail)
- Cannot deactivate or delete the key you're currently using
- **Rate limiting** on all endpoints (protection against brute force)
- **Audit logging** for all key operations (complete trail)
- **IP whitelisting** for sensitive keys (restrict by IP address)
- **Key rotation** support (automated workflow)
- **Monitoring** with structured logging (security events)

See [API Key Security Documentation](docs/API_KEY_SECURITY.md) for detailed security features.

## 🧪 Testing

- **82 tests** covering all features (all passing)
- **Service layer tests**: Business logic validation
- **Router tests**: HTTP endpoint behavior
- **Database tests**: Model relationships and constraints
- **API Key tests**: Authentication, authorization, and security features
- **Security tests**: Rate limiting, audit logging, IP whitelisting

```bash
# Run all tests
uv run pytest -v

# Run with coverage report
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

## 🛠️ Tech Stack

- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM and database
- **Bcrypt** - Password hashing
- **slowapi** - Rate limiting
- **Pytest** - Testing framework
- **SQLite** - Database (easily swappable)

## 📦 Project Structure

```
octopus/
├── app/
│   ├── api/v1/           # API routing
│   ├── core/             # Config and security
│   ├── db/               # Database models
│   └── features/         # Feature modules
│       ├── conversations/
│       └── users/
├── tests/                # Test suite
│   ├── api/
│   ├── db/
│   └── features/
├── docs/                 # Documentation
└── pyproject.toml        # Dependencies
```

## 🚢 Docker Support

```bash
# Build the Docker image
docker build -t octopus .

# Run the container
docker run -p 8000:80 octopus
```

## 🤝 Contributing

1. Read the [Feature Implementation Guide](docs/FEATURE_IMPLEMENTATION_GUIDE.md)
2. Follow the [Best Practices](docs/BEST_PRACTICES.md)
3. Write tests for all new features
4. Ensure all tests pass before submitting

## 📝 License

See [LICENSE](LICENSE) file for details.