# Test README

## Running Tests

To run all tests with `uv`:

```bash
# Install test dependencies
uv sync --extra test

# Or add test dependencies individually
uv add --dev pytest pytest-cov httpx

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test directory
uv run pytest tests/features/conversations/

# Run specific test file
uv run pytest tests/features/conversations/test_router.py

# Run specific test
uv run pytest tests/features/conversations/test_router.py::test_create_conversation

# Run with verbose output
uv run pytest -v

# Run and stop on first failure
uv run pytest -x
```

## Test Structure

Tests now mirror the app structure:

```
tests/
├── conftest.py                          # Shared fixtures and test configuration
├── api/                                 # API tests
│   └── v1/
│       └── test_endpoints.py           # API v1 endpoint tests
├── features/                            # Feature tests
│   └── conversations/
│       ├── test_router.py              # Conversation router/endpoint tests
│       └── test_service.py             # Conversation service layer tests
└── db/
    └── test_models.py                  # Database model tests
```

## Test Coverage

Tests cover:
- ✅ API endpoints and authentication
- ✅ Health checks
- ✅ CRUD operations for conversations
- ✅ Service layer methods
- ✅ Adding and retrieving messages
- ✅ Database model relationships
- ✅ Cascade deletion
- ✅ Error handling (404s, validation errors)
- ✅ Public vs protected endpoints
- ✅ Pagination
