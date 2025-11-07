# 🐙 Octopus CLI

<div align="center">

### *The AI-Friendly FastAPI Architecture Generator*

**Stop wrestling with project structure. Start building features.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com/)
[![Typer](https://img.shields.io/badge/Typer-CLI-purple.svg)](https://typer.tiangolo.com/)
[![UV](https://img.shields.io/badge/UV-package%20manager-orange.svg)](https://github.com/astral-sh/uv)

</div>

---

## ⚡ Why Octopus?

**Traditional FastAPI project setup:**
```bash
mkdir my-api && cd my-api
touch main.py requirements.txt
# ... 30 minutes of boilerplate later ...
```

**With Octopus:**
```bash
octopus init
uv run fastapi dev
uv run pytest
# ✨ Production-ready FastAPI app in 2 seconds
```

### 🎯 Built for Modern Development

🤖 **AI-First Design** - Structure so clean that AI assistants understand it instantly  
🚀 **Zero Config** - No manual imports, no router mounting, no configuration hell  
🎨 **Beautiful DX** - Rich CLI with colors, trees, and helpful feedback  
♾️ **Infinite Nesting** - Features inside features, as deep as you need  
🧅 **Onion Architecture** - Clean layers: Router → Service → Entities/Schemas  
🔄 **Auto-Discovery** - Add a feature, it's instantly available in your API  
✨ **Path Syntax** - Create nested features from anywhere: `octopus add feature users/profile`  
📦 **Modern Stack** - FastAPI + UV + Pydantic + Your choice of DB/Auth

## 🎬 See It In Action

```bash
# Create your app
octopus init
cd app

# Add features - they auto-mount to your API
octopus add feature users
octopus add feature products

# Add shared modules - instantly available everywhere
octopus add shared database
octopus add shared auth

# Navigate anywhere, add nested features
cd app/users
octopus add feature profile
octopus add feature settings

# Or use path syntax - no need to navigate!
octopus add feature products/inventory
octopus add feature users/profile/avatar

# Visualize your structure
octopus structure
```

**Beautiful visualization:**
```
🐙 test_app/
└── 🏠 app/
    ├── ⚡ products/ (1 route)
    │   ├── GET /status Get status of the products feature.
    │   └── ⚡ inventory/ (1 route)
    │       └── GET /status Get status of the inventory feature.
    ├── ⚡ users/ (1 route)
    │   ├── GET /status Get status of the users feature.
    │   └── ⚡ profile/ (1 route)
    │       ├── GET /status Get status of the profile feature.
    │       └── ⚡ avatar/ (1 route)
    │           └── GET /status Get status of the avatar feature.
    ├── 📦 auth/
    ├── 📦 config/
    ├── 📦 database/
    └── 📦 routing/

📊 Statistics: 5 features • 4 shared modules • 5 routers • 9 services
```

**Run it:**
```bash
# Run it
uv run fastapi dev
```

**Result:** Fully working API with routes:
- `GET /users/` ✅
- `GET /users/profile/` ✅  
- `GET /users/settings/` ✅
- `GET /products/` ✅

**No manual configuration. No imports. No routing setup. It just works.**

---

## 📖 What Is Octopus?

Octopus is a production-ready CLI tool that generates well-structured FastAPI applications following a **recursive fractal onion architecture**. 

🤖 **AI-Friendly by Design** - Created specifically to be understood by AI assistants while maintaining high structural quality. Clear separation of concerns, consistent patterns, and self-documenting structure make it ideal for AI-assisted development with GitHub Copilot, ChatGPT, or any coding assistant.

Every component (app, feature, shared module) can contain nested features and shared modules, creating a self-similar structure at any depth.

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

---

## 🚀 Quick Start

### Install

**Requirements:** Python 3.10+ and [UV package manager](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/Tom-Laurent-TL/octopus.git
cd octopus
uv venv && .venv\Scripts\Activate.ps1
uv pip install -e .
```

### Create Your First App

```bash
octopus init --path your/path/my-project (will create the path if needed)
uv run fastapi dev
```

🎉 **That's it!** Open http://localhost:8000 - your API is live!

### Build Something Real

```bash
# Add user management
octopus add feature users
octopus add shared database

# Add nested features - two ways:
# 1. Navigate into the feature
cd app/users
octopus add feature authentication
octopus add feature profile

# 2. Or use path syntax from anywhere
octopus add feature users/settings
octopus add feature users/profile/avatar

# View your structure
octopus structure --routes
```

---

## 📚 Documentation

Every generated app includes comprehensive guides:

| Guide | What You'll Learn |
|-------|------------------|
| **ARCHITECTURE.md** | Complete architecture explanation, fractal structure, auto-discovery |
| **BEST_PRACTICES.md** | Service patterns, dependency injection, error handling, security |
| **EXAMPLES.md** | Full CRUD example, nested features, JWT auth, database setup |

```bash
cd my-api
cat docs/ARCHITECTURE.md      # Start here!
```

---

## 🎓 Deep Dive

<details>
<summary><b>📋 Available Commands</b></summary>

### Initialize Application

```bash
# Initialize a new FastAPI application with full architecture
octopus init

# Initialize in a specific directory
octopus init --path my-api
```

Creates a complete FastAPI project with:
- Main app with config as a shared module
- Comprehensive documentation (ARCHITECTURE.md, BEST_PRACTICES.md, EXAMPLES.md)
- Test structure with example health check test
- Placeholder TODO files for planning
- UV package management setup
- Ready-to-run FastAPI application

### Add Feature

```bash
# Add a feature module (context-aware)
octopus add feature <NAME>

# Examples
octopus add feature users           # In app root - creates app/users/
octopus add feature hello_world     # Inside features/users/ - creates nested feature

# Or use path syntax from anywhere (no need to cd!)
octopus add feature users/profile   # Creates app/users/features/profile/
octopus add feature users/profile/settings  # Deeply nested!
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

### Remove Feature or Shared Module

```bash
# Remove a feature (context-aware)
octopus remove feature <NAME>

# Remove a shared module (context-aware)
octopus remove shared <NAME>

# Examples
octopus remove feature users
octopus remove shared database
```

Safely removes features or shared modules, including:
- All files and directories
- Nested features and shared modules
- Updates imports in sibling units

### Display Project Structure

```bash
# Display a rich tree view of your project structure
octopus structure

# Show full structure with all files
octopus structure --full

# Show API routes
octopus structure --routes
```

Visualizes your Octopus project with:
- Color-coded features and shared modules
- Nesting depth indicators
- Optional route mapping
- File and directory counts

</details>

<details>
<summary><b>🏗️ Generated Project Structure</b></summary>

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

</details>

<details>
<summary><b>🛠️ Technology Stack</b></summary>

### CLI
- **Typer** - Modern CLI framework with beautiful terminal output and Rich integration
- **Rich** - Beautiful terminal formatting, colors, and progress indicators
- **Python 3.10+** - Modern Python features

### Generated Applications
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management
- **Pydantic-Settings** - Environment-based configuration
- **UV** - Fast Python package manager
- **SQLAlchemy** - ORM (in documentation examples)
- **Python-Jose** - JWT tokens (in auth examples)
- **Bcrypt** - Password hashing (in auth examples)

</details>

<details>
<summary><b>⚡ Shell Autocompletion</b></summary>

Enable tab completion for your shell:

**PowerShell:**
```powershell
octopus --install-completion powershell
# Restart your terminal
```

**Bash:**
```bash
octopus --install-completion bash
source ~/.bashrc
```

**Zsh:**
```zsh
octopus --install-completion zsh
source ~/.zshrc
```

**Fish:**
```fish
octopus --install-completion fish
# Restart your terminal
```

After installation, press TAB to autocomplete commands, subcommands, and options!

</details>

---

## ✅ What's Implemented

- ✅ **Full app scaffolding** with recursive structure
- ✅ **Feature generation** with Service class pattern
- ✅ **Shared module generation** with auto-imports
- ✅ **Context-aware commands** (detects current location)
- ✅ **Auto-discovery system** (no manual router mounting)
- ✅ **Comprehensive documentation** (3 markdown guides per app)
- ✅ **Test structure generation** with examples
- ✅ **Remove commands** for features and shared modules
- ✅ **Structure visualization** with rich tree display
- ✅ **UV package management** integration
- ✅ **Shell autocompletion** support
- ✅ **On-demand directory creation** (no empty folders)
- ✅ **Absolute imports** (works at any nesting depth)

## 🔮 Roadmap

- [ ] **CI/CD templates** - GitHub Actions, GitLab CI workflows
- [ ] **Database migration integration** - Alembic setup and templates
- [ ] **Docker configuration** - Dockerfile and docker-compose templates

---

## 🙋 Getting Help

```bash
# General help
octopus --help

# Command-specific help
octopus init --help
octopus add --help
octopus add feature --help
octopus add shared --help
octopus remove --help
octopus structure --help
```

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- Enhanced test generation for features
- Additional documentation templates
- Database migration templates
- Docker and CI/CD configurations
- Improved error handling
- Add tests for the CLI itself
- Plugin system development

---

<div align="center">

**Built with 🤖 AI-First thinking | Made for developers who ❤️ clean architecture**

⭐ **Star us on GitHub** if Octopus makes your FastAPI development easier!

[Report Bug](https://github.com/Tom-Laurent-TL/octopus/issues) • [Request Feature](https://github.com/Tom-Laurent-TL/octopus/issues) • [Contribute](https://github.com/Tom-Laurent-TL/octopus/pulls)

</div>

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for FastAPI developers**
