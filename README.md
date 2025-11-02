# Octopus

A production-ready FastAPI application with feature-based architecture, comprehensive testing, and clean separation of concerns.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Tom-Laurent-TL/octopus.git
cd octopus

# Install dependencies
uv sync
uv sync --extra test
```

### Configuration

Create a `.env` file in the project root:

```env
MASTER_API_KEY=your-secret-api-key-here
DATABASE_URL=sqlite:///./data/chat_conversations.db
```

**Note**: Database is stored in the `data/` folder for clean organization and consistency with Docker setup. See [Docker Deployment Guide](docs/DOCKER_DEPLOYMENT.md) for details.

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
  - Multi-user participation support
  - Cascade deletion support

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

## 🗄️ Database Migrations

This project uses **[Alembic](https://alembic.sqlalchemy.org/)** for database schema migrations.

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Check current migration version
uv run alembic current

# Create a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Rollback one migration
uv run alembic downgrade -1
```

**First time setup** (if you already have a database):
```bash
# Mark existing database as at current baseline
uv run alembic stamp head
```

For comprehensive migration guides, see [Database Migrations Documentation](docs/DATABASE_MIGRATIONS.md).

## 🧪 Testing

- **77 tests** covering all features (all passing)
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

## 🚢 Docker Deployment

### Quick Start

**1. Build and Start Container:**

```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# View logs
docker-compose logs -f
```

**2. Bootstrap (First Time Only):**

```bash
# Create your master API key
curl -X POST http://localhost:8000/bootstrap

# Or on Windows PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/bootstrap" -Method Post
```

**3. Save Your API Key:**

Update your `.env` file with the returned API key:

```env
MASTER_API_KEY=octopus_abc123...your-actual-key
# Local development database path
DATABASE_URL=sqlite:///./chat_conversations.db
# Docker database path (uncomment when running in Docker)
# DATABASE_URL=sqlite:////app/data/chat_conversations.db
```

> **Note**: You can keep the local `DATABASE_URL` - Docker Compose automatically overrides it with the correct path. Or uncomment the Docker line if you prefer explicit configuration.

**4. Restart to Apply:**

```bash
docker-compose restart
```

**5. Access the API:**

- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000
- **Health**: http://localhost:8000/health

### Docker Features

✅ **Automatic Database Migrations** - Schema updates on startup  
✅ **Persistent Storage** - Database saved in `./data/` directory  
✅ **Environment Override** - `.env` works for both local and Docker  
✅ **Health Checks** - Built-in container health monitoring  
✅ **Volume Mount** - Easy backup and restore  

### Using Docker Directly

```bash
# Build the image
docker build -t octopus .

# Run with persistent volume
docker run -d -p 8000:80 -v $(pwd)/data:/app/data --name octopus-api octopus

# Windows PowerShell:
docker run -d -p 8000:80 -v ${PWD}/data:/app/data --name octopus-api octopus
```

### Database Management

**Backup Database:**
```bash
# Docker Compose
cp ./data/chat_conversations.db ./backup_$(date +%Y%m%d).db

# Windows PowerShell
Copy-Item .\data\chat_conversations.db .\backup_$(Get-Date -Format 'yyyyMMdd').db
```

**Reset Database:**
```bash
# Stop container
docker-compose down

# Delete database
rm -rf ./data/chat_conversations.db

# Start fresh
docker-compose up -d
curl -X POST http://localhost:8000/bootstrap
```

**Automatic Migrations:**

The application automatically runs database migrations on startup to ensure schema compatibility. If you update the code:

```bash
# Just rebuild and restart - migrations run automatically
docker-compose up -d --build
```

### Environment Configuration

Your `.env` file works for **both** local development and Docker:

```env
MASTER_API_KEY=your-master-key-here
# Local development database path
DATABASE_URL=sqlite:///./chat_conversations.db
# Docker database path (uncomment when running in Docker)
# DATABASE_URL=sqlite:////app/data/chat_conversations.db
```

**Two Options:**

1. **Keep local path (Recommended)** - Docker Compose automatically overrides `DATABASE_URL` with the correct Docker path. No manual changes needed!

2. **Uncomment Docker path** - If running exclusively in Docker, uncomment the Docker `DATABASE_URL` line and comment out the local one.

| Environment | Database Path | Configured By |
|-------------|---------------|---------------|
| Local (`uv run`) | `./data/chat_conversations.db` | `.env` file |
| Docker Compose | `./data/chat_conversations.db` | `docker-compose.yml` |

### Troubleshooting

**Database Schema Errors:**
```bash
# Migrations run automatically on startup
docker-compose restart
```

**Port Already in Use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8001:80"  # Use 8001 instead of 8000
```

**View Container Logs:**
```bash
docker-compose logs -f
```

**Check Container Status:**
```bash
docker-compose ps
```

📚 **Complete Docker guide with production deployment**: [Docker Deployment Guide](docs/DOCKER_DEPLOYMENT.md)

## 🤝 Contributing

1. Read the [Feature Implementation Guide](docs/FEATURE_IMPLEMENTATION_GUIDE.md)
2. Follow the [Best Practices](docs/BEST_PRACTICES.md)
3. Write tests for all new features
4. Ensure all tests pass before submitting

## 📝 License

See [LICENSE](LICENSE) file for details.