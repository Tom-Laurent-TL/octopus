# 🐙 Octopus CLI

> A powerful FastAPI project generator with recursive fractal onion architecture

## 📖 Overview

Octopus is a production-ready CLI tool that generates well-structured FastAPI applications following a **recursive fractal onion architecture**. Every component (app, feature, shared module) can contain nested features and shared modules, creating a self-similar structure at any depth.

### Key Features

✨ **Recursive Architecture** - Features can contain sub-features infinitely deep  
🧅 **Onion Layer Pattern** - Clear separation: Router → Service → Entities/Schemas  
🔄 **Auto-Discovery** - Routers automatically mount without manual configuration  
📦 **Context-Aware** - Commands detect where you are in the project structure  
🎯 **Service Layer Pattern** - Business logic isolated from routing and data layers  
🌊 **Cascading Shared Modules** - App-level utilities available at any depth  
📚 **Comprehensive Docs** - Every app includes architecture guides and examples  
🔧 **UV Package Manager** - Modern Python dependency management  
⚡ **Tab Completion** - Shell autocompletion support for all commands

## 🚀 Installation

### Prerequisites

- Python 3.10+ (tested with 3.13)
- [UV package manager](https://github.com/astral-sh/uv) installed

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd cli_project

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install in editable mode
uv pip install -e .
```

After installation, the `octopus` command is available in your terminal (with virtual environment activated).

### Shell Autocompletion (Optional)

Enable tab completion for your shell:

**PowerShell:**
```powershell
octopus --install-completion powershell
# Restart your terminal
```

**Bash:**
```bash
octopus --install-completion bash
# Then run: source ~/.bashrc
```

**Zsh:**
```zsh
octopus --install-completion zsh
# Then run: source ~/.zshrc
```

**Fish:**
```fish
octopus --install-completion fish
# Restart your terminal
```

After installation, you can press TAB to autocomplete commands, subcommands, and options!

## 📋 Available Commands

### Create Application

```bash
# Create a new FastAPI application with full architecture
octopus create app <NAME>

# Example
octopus create app my-api
```

Creates a complete FastAPI project with:
- Main app with config as a shared module
- Comprehensive documentation (ARCHITECTURE.md, BEST_PRACTICES.md, EXAMPLES.md)
- UV package management setup
- Ready-to-run FastAPI application

### Add Feature

```bash
# Add a feature module (context-aware)
octopus add feature <NAME>

# Examples
octopus add feature users           # In app root - creates app/users/
octopus add feature hello_world     # Inside features/users/ - creates nested feature
```

Creates:
- Router with automatic mounting
- Service class for business logic
- `entities.py` for database models
- `schemas.py` for API models
- Auto-imports for sibling shared modules (commented)
- On-demand `features/` and `shared/` subdirectories

### Add Shared Module

```bash
# Add a shared module (context-aware)
octopus add shared <NAME>

# Examples
octopus add shared database         # Creates shared/database/
octopus add shared auth            # Creates shared/auth/
```

Creates:
- Service class pattern
- Automatically updates all sibling features with import comments
- Special handling for `config` module (includes Settings class)

### 🚧 Coming Soon

```bash
# Generate test stubs (placeholder)
octopus stub tests

# Generate documentation stubs (placeholder)
octopus stub docs

# Display project structure tree (placeholder)
octopus structure
```

## 🎯 Quick Start Example

```bash
# 1. Create a new application
octopus create app my-api
cd my-api

# 2. Run the app (it works immediately!)
uv run fastapi dev app/main.py

# 3. Add a users feature
octopus add feature users

# 4. Navigate into users and add a nested feature
cd app/users
octopus add feature profile

# 5. Add shared modules
cd ../..  # Back to app root
octopus add shared database
octopus add shared auth

# 6. Add shared module to nested feature
cd app/users
octopus add shared validation

# Routes are automatically mounted:
# GET /users/         -> app/users/router.py
# GET /users/profile/ -> app/users/features/profile/router.py
```

## 🏗️ Generated Project Structure

```
my-api/
├── app/
│   ├── __init__.py          # Auto-discovery: mounts all features & shared
│   ├── main.py              # FastAPI app entry point
│   ├── router.py            # Root API router
│   ├── users/               # Feature (created with: octopus add feature users)
│   │   ├── __init__.py      # Auto-mounts sub-features & shared modules
│   │   ├── router.py        # Routes: /users/*
│   │   ├── service.py       # Business logic (UsersService class)
│   │   ├── entities.py      # Database models (SQLAlchemy)
│   │   ├── schemas.py       # API models (Pydantic)
│   │   ├── features/        # Nested features (created on-demand)
│   │   │   └── profile/     # Sub-feature: /users/profile/*
│   │   │       ├── router.py
│   │   │       ├── service.py
│   │   │       └── ...
│   │   └── shared/          # Feature-scoped shared modules
│   │       └── validation/  # Shared within users feature
│   └── shared/              # App-level shared modules
│       ├── config/          # Configuration (created by default)
│       │   ├── __init__.py
│       │   └── service.py   # Settings class + ConfigService
│       ├── database/        # (created with: octopus add shared database)
│       │   ├── __init__.py
│       │   └── service.py   # DatabaseService class
│       └── auth/            # (created with: octopus add shared auth)
│           ├── __init__.py
│           └── service.py   # AuthService class
├── docs/
│   ├── ARCHITECTURE.md      # Complete architecture guide
│   ├── BEST_PRACTICES.md    # Coding standards & patterns
│   └── EXAMPLES.md          # Real-world implementation examples
├── pyproject.toml           # UV package configuration
└── uv.lock                  # Locked dependencies
```

### Key Architecture Principles

🔁 **Recursive Structure** - Every unit (app, feature) can contain:
- `features/` - Nested features (self-similar structure)
- `shared/` - Shared modules for that scope
- Standard files: `router.py`, `service.py`, `entities.py`, `schemas.py`

🧅 **Onion Layers** (dependency direction: →)
```
Router → Service → Entities/Schemas
```

🚀 **Auto-Discovery** - No manual imports needed:
- `app/__init__.py` auto-mounts all features
- Feature `__init__.py` auto-mounts sub-features
- Uses centralized `auto_discover_routers()` utility

🌊 **Cascading Shared Modules** - The killer feature:
```python
app/shared/config/     # Automatically available to ALL features
app/shared/database/   # At ANY nesting depth

# Even deeply nested features have access (absolute imports):
# app/features/users/features/profile/features/avatar/__init__.py
# from app.shared.config.service import settings    ✅ Works!
# from app.shared.database.service import get_db    ✅ Works!

# No more unreadable relative imports like:
# from ......shared.config import settings  ❌ Avoid this!
```

📦 **Service Layer Pattern** - All business logic in `XxxService` classes:
```python
class UsersService:
    def get_all(self): ...
    def create(self, data): ...
```

## 🛠️ Technology Stack

### CLI
- **Typer** - CLI framework with Rich styling
- **Python 3.10+** - Modern Python features

### Generated Applications
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management
- **Pydantic-Settings** - Environment-based configuration
- **UV** - Fast Python package manager
- **SQLAlchemy** - ORM (in documentation examples)
- **Python-Jose** - JWT tokens (in auth examples)
- **Bcrypt** - Password hashing (in auth examples)

## ✅ What's Implemented

- ✅ **Full app scaffolding** with recursive structure
- ✅ **Feature generation** with Service class pattern
- ✅ **Shared module generation** with auto-imports
- ✅ **Context-aware commands** (detects current location)
- ✅ **Auto-discovery system** (no manual router mounting)
- ✅ **Comprehensive documentation** (3 markdown guides per app)
- ✅ **UV package management** integration
- ✅ **Shell autocompletion** support
- ✅ **On-demand directory creation** (no empty folders)
- ✅ **Relative imports** (works at any nesting depth)

## 🔮 Roadmap

- [ ] **Test stub generation** - Auto-generate test files for features
- [ ] **Documentation stubs** - Generate API documentation from code
- [ ] **Structure visualization** - Display project tree
- [ ] **Migration tools** - Convert existing projects to Octopus structure
- [ ] **Plugin system** - Custom generators and templates
- [ ] **Interactive mode** - Guided project creation
- [ ] **Template customization** - User-defined code templates
- [ ] **CI/CD templates** - GitHub Actions, GitLab CI workflows

## 📚 Documentation

Every generated app includes comprehensive documentation in the `docs/` folder:

- **ARCHITECTURE.md** - Complete architecture explanation, fractal structure, auto-discovery, nesting guidelines
- **BEST_PRACTICES.md** - Service patterns, dependency injection, error handling, security, testing
- **EXAMPLES.md** - Full CRUD example, nested features, JWT authentication, database setup

## 🎓 Learning Resources

After creating an app with `octopus create app my-api`, read the generated docs:

```bash
cd my-api
cat docs/ARCHITECTURE.md      # Understand the structure
cat docs/BEST_PRACTICES.md    # Learn coding patterns
cat docs/EXAMPLES.md          # See real implementations
```

## 🙋 Getting Help

```bash
# General help
octopus --help

# Command-specific help
octopus create --help
octopus add --help
octopus add feature --help
octopus add shared --help
```

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- Implement remaining commands (stub tests, stub docs, structure)
- Add more documentation examples
- Create custom templates
- Improve error handling
- Add tests for the CLI itself

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for FastAPI developers**
