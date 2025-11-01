# Documentation

Welcome to the FastAPI App documentation! This folder contains comprehensive guides for developing and maintaining this application.

## 📚 Documentation Index

### For Developers

1. **[Feature Implementation Guide](FEATURE_IMPLEMENTATION_GUIDE.md)** 🚀
   - Complete step-by-step guide to implementing new features
   - Code examples for all layers (models, schemas, services, routers)
   - Testing patterns and best practices
   - Implementation checklist
   - **Start here when building new features**

2. **[Best Practices](BEST_PRACTICES.md)** 💡
   - Real-world mistakes and solutions
   - Lessons learned from actual development
   - Dependency management strategies
   - Testing patterns that work
   - Debugging workflows
   - **Read this to avoid common pitfalls**

3. **[Project Architecture](PROJECT_STRUCTURE.md)** 🏗️
   - Complete project organization overview
   - Feature-based architecture explanation
   - Directory structure reference
   - Current features documentation
   - Database schema and relationships

## 🎯 Quick Navigation

### I want to...

- **Build a new feature** → [Feature Implementation Guide](FEATURE_IMPLEMENTATION_GUIDE.md)
- **Understand the codebase** → [Project Architecture](PROJECT_STRUCTURE.md)
- **Avoid common mistakes** → [Best Practices](BEST_PRACTICES.md)
- **Write tests** → See testing sections in [Feature Implementation Guide](FEATURE_IMPLEMENTATION_GUIDE.md)
- **Debug an issue** → Check debugging section in [Best Practices](BEST_PRACTICES.md)

## 📖 Reading Order for New Developers

1. **[Project Architecture](PROJECT_STRUCTURE.md)** - Understand how the project is organized
2. **[Best Practices](BEST_PRACTICES.md)** - Learn from past mistakes
3. **[Feature Implementation Guide](FEATURE_IMPLEMENTATION_GUIDE.md)** - Build your first feature

## 🔑 Key Concepts

### Architecture Layers

```
Router Layer (HTTP)
    ↓
Service Layer (Business Logic)
    ↓
Model Layer (Database)
```

- **Routers**: Handle HTTP requests/responses, call service methods
- **Services**: Contain business logic and database operations
- **Models**: Define database schema and relationships
- **Schemas**: Validate and serialize data (Pydantic)

### Feature-Based Structure

```
app/features/<feature_name>/
├── router.py      # HTTP endpoints
├── service.py     # Business logic
└── schemas.py     # Data validation
```

Each feature is self-contained and independent.

### Many-to-Many Relationships

The application uses **many-to-many relationships** for conversations, allowing multiple users to participate in the same conversation (1-on-1 chats, group conversations, channels, etc.).

**Key implementation:**
- Association table (`conversation_participants`) links users and conversations
- Service layer methods handle adding/removing participants dynamically
- Supports flexible conversation models (private chats, group discussions)
- **Message tracking**: Each message records which user sent it (with participant validation)

See [Best Practices - Many-to-Many Relationships](BEST_PRACTICES.md#-best-practice-many-to-many-relationships) for implementation details.

### Testing Philosophy

- Test both router (HTTP) and service (logic) layers
- Tests mirror application structure
- Use in-memory database for isolation
- Explicitly test authentication requirements

## 🛠️ Common Commands

```bash
# Run all tests
uv run pytest -v

# Run specific feature tests
uv run pytest tests/features/users/ -v

# Check code coverage
uv run pytest --cov=app --cov-report=html

# Start development server
uv run fastapi dev app/main.py

# Install dependencies
uv sync
uv sync --extra test
```

## 📋 Development Workflow

1. **Plan** - Sketch data model and relationships
2. **Model** - Create SQLAlchemy models
3. **Schema** - Define Pydantic schemas
4. **Service** - Implement business logic
5. **Router** - Create HTTP endpoints
6. **Test** - Write service and router tests
7. **Verify** - Run full test suite

See [Feature Implementation Guide](FEATURE_IMPLEMENTATION_GUIDE.md) for detailed steps.

## 🤝 Contributing

When adding documentation:

1. Keep it practical with real examples
2. Update this README with links to new docs
3. Follow existing formatting conventions
4. Include code examples where helpful

## 📝 Documentation Maintenance

- **Update when**: Adding features, changing architecture, learning new lessons
- **Review**: Before major releases
- **Keep current**: Documentation should match codebase

---

**Last Updated**: November 1, 2025

**Questions?** Check the relevant guide or reach out to the team.
