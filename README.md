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
API_KEY=your-secret-api-key-here
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
├── core/              # Configuration and security
├── db/                # Database models and setup
├── features/          # Feature modules
│   ├── conversations/ # Chat conversation feature
│   └── users/        # User management feature
└── api/v1/           # API version routing
```

### Key Principles

- **Feature-based structure**: Each feature is self-contained
- **Service layer pattern**: Business logic separated from HTTP concerns
- **Comprehensive testing**: Both unit and integration tests
- **Type safety**: Full type hints with Pydantic validation

## 🔑 Features

### Production Features

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

### Authentication

API uses header-based authentication:

**Linux/Mac/WSL:**
```bash
curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/api/v1/users/
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/" -Headers @{"X-API-Key"="your-secret-api-key"}

# Or use the included test script
.\scripts\test-api.ps1
```

**Or use the interactive API docs at** http://localhost:8000/docs

## 🧪 Testing

- **46 tests** covering all features
- **Service layer tests**: Business logic validation
- **Router tests**: HTTP endpoint behavior
- **Database tests**: Model relationships and constraints

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