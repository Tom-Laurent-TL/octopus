"""
Templates for generating Octopus project files.
"""


def get_root_router_template():
    """Template for the root router with auto-mounting."""
    return '''from fastapi import APIRouter
from app.shared.routing import auto_discover_routers

router = APIRouter()

# Automatically mount routers from direct sub-features
auto_discover_routers(router, __file__, __package__)
'''


def get_router_template():
    """Template for a feature router."""
    return '''from fastapi import APIRouter

router = APIRouter()

# TODO: Add your routes here
'''


def get_service_template():
    """Template for a service layer."""
    return '''"""
Business logic for this unit.
"""

# TODO: Add your service functions here
'''


def get_entities_template():
    """Template for entities/models."""
    return '''"""
Domain entities or ORM models for this unit.
"""

# TODO: Define your entities/models here
'''


def get_schemas_template():
    """Template for Pydantic schemas."""
    return '''"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel

# TODO: Define your schemas here
'''


def get_main_template():
    """Template for main.py."""
    return '''from fastapi import FastAPI
from app.router import router

app = FastAPI(title="🐙 Octopus App")

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include all feature routers (automatically mounted)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


def get_config_template():
    """Template for config.py."""
    return '''from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    app_name: str = "Octopus App"
    environment: str = "development"
    database_url: str | None = None

settings = Settings()
'''


def get_env_example_template():
    """Template for .env.example."""
    return '''APP_NAME="Octopus App"
ENVIRONMENT="development"
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
'''


def get_readme_template(unit_name: str = None):
    """Template for unit README.md."""
    name = unit_name if unit_name else "App"
    return f'''# {name} Unit

This is an Octopus Unit following the recursive fractal architecture.

## Structure

- `router.py` - FastAPI routes and automatic sub-feature mounting
- `service.py` - Business logic
- `entities.py` - Domain models
- `schemas.py` - Pydantic schemas
- `features/` - Child feature units (recursive)
- `shared/` - Shared utilities (recursive)

## Usage

Add features with:
```bash
octopus add feature <name>
```

Add shared modules with:
```bash
octopus add shared <name>
```

## Documentation

See `/docs` and `/redoc` when the app is running.
'''


def get_todo_template(unit_name: str = None):
    """Template for unit TODO.md."""
    name = unit_name if unit_name else "App"
    return f'''# TODO - {name}

- [ ] Define your entities in `entities.py`
- [ ] Create Pydantic schemas in `schemas.py`
- [ ] Implement business logic in `service.py`
- [ ] Add routes in `router.py`
- [ ] Write tests for this unit
- [ ] Document API endpoints
'''


def get_root_readme_template():
    """Template for project root README.md."""
    return '''# 🐙 Octopus App

A FastAPI application built with the Octopus recursive fractal architecture.

## Architecture

This project follows the **Octopus** pattern where every component is a self-contained unit with:
- `router.py` - FastAPI routes with automatic sub-feature mounting
- `service.py` - Business logic
- `entities.py` - Domain models
- `schemas.py` - Pydantic schemas
- `features/` - Recursive child features
- `shared/` - Recursive shared utilities

## Quick Start

```bash
# Install dependencies (already done during init)
uv sync

# Run the application
uv run fastapi dev

# Or with uvicorn directly
uv run uvicorn app.main:app --reload
```

Visit:
- **http://localhost:8000/health** - Health check endpoint
- **http://localhost:8000/docs** - Interactive API documentation (Swagger UI)
- **http://localhost:8000/redoc** - Alternative API documentation (ReDoc)

## Development Commands

```bash
# Add a new feature
octopus add feature users
octopus add feature auth/permissions  # Nested feature

# Add a shared module
octopus add shared database
octopus add shared utils/validators   # Nested shared

# Remove components
octopus remove feature users
octopus remove shared database

# View project structure with routes
octopus structure

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app
```

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── router.py            # Auto-mounting root router
├── __init__.py          # Exports: settings, auto_discover_routers
├── features/            # Feature modules (recursive)
│   └── <feature>/
│       ├── router.py
│       ├── service.py
│       ├── entities.py
│       ├── schemas.py
│       ├── README.md
│       ├── TODO.md
│       ├── features/    # Nested features
│       └── shared/      # Nested shared modules
└── shared/              # Shared utilities (recursive)
    ├── config/          # Application settings
    │   └── service.py   # Settings, settings instance
    └── routing/         # Auto-discovery utilities
        └── service.py   # auto_discover_routers function

tests/                   # Mirrors app/ structure
├── conftest.py          # Test fixtures (client fixture)
└── app/
    ├── test_health.py   # Health endpoint tests
    ├── features/        # Feature tests
    └── shared/          # Shared module tests

docs/                    # Documentation
├── ARCHITECTURE.md      # Architecture guide
├── BEST_PRACTICES.md    # Coding standards
└── EXAMPLES.md          # Real-world examples

.env.example             # Environment variables template
```

## Default Shared Modules

Every new app includes two essential shared modules:

### `shared/config/`
Application configuration using pydantic-settings:
```python
from app.shared.config import settings

# Access configuration
print(settings.app_name)
print(settings.environment)
print(settings.database_url)
```

### `shared/routing/`
Router auto-discovery utility:
```python
from app.shared.routing import auto_discover_routers

router = APIRouter(prefix="/users")
# ... add routes ...

# Automatically mount nested feature routers
auto_discover_routers(router, __file__, __package__)
```

## Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
APP_NAME="My Octopus App"
ENVIRONMENT="development"
DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

3. Access in code:
```python
from app import settings

print(settings.app_name)  # "My Octopus App"
```

## Testing

Run the test suite:
```bash
# All tests
uv run pytest

# With output
uv run pytest -v

# With coverage
uv run pytest --cov=app --cov-report=html

# Specific test file
uv run pytest tests/app/test_health.py

# Watch mode (requires pytest-watch)
uv run ptw
```

## Adding Features

```bash
# Create a users feature
octopus add feature users

# This creates:
# - app/features/users/ (router, service, entities, schemas)
# - tests/app/features/users/ (test files)
# - docs/app/features/users/ (documentation)

# Add nested features
octopus add feature users/profile
octopus add feature users/settings
```

## Learn More

- **`docs/ARCHITECTURE.md`** - Detailed architecture guide
- **`docs/BEST_PRACTICES.md`** - Coding standards and patterns
- **`docs/EXAMPLES.md`** - Real-world implementation examples
- **`TODO.md`** - Project tasks and next steps
- Each feature has its own `README.md` and `TODO.md`

## Support

Generated with [Octopus CLI](https://github.com/yourusername/octopus) 🐙
'''


def get_root_todo_template():
    """Template for project root TODO.md."""
    return '''# TODO

- [ ] Add your first feature with `octopus add feature <name>`
- [ ] Configure environment variables in `.env`
- [ ] Define your entities and schemas
- [ ] Write your first service logic
- [ ] Add tests
- [ ] Update documentation
'''


def get_tests_readme_template():
    """Template for tests README.md."""
    return '''# Tests

Mirrors the app/ structure.

## Running Tests

```bash
uv run pytest
```
'''


def get_tests_todo_template():
    """Template for tests TODO.md."""
    return '''# TODO - Tests

- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add test coverage reporting
'''


def get_docs_readme_template():
    """Template for docs README.md."""
    return "# App Documentation\n\nMirrors the app/ structure.\n"


def get_docs_todo_template():
    """Template for docs TODO.md."""
    return "# TODO - Docs\n\n- [ ] Document API endpoints\n- [ ] Add architecture diagrams\n"


def get_feature_router_template(feature_name: str, class_name: str):
    """Template for feature router with service class."""
    return f'''from fastapi import APIRouter
from app.shared.routing import auto_discover_routers
from .service import {class_name}Service

router = APIRouter(prefix="/{feature_name}", tags=["{feature_name}"])

service = {class_name}Service()


@router.get("/status")
def get_status():
    """Get status of the {feature_name} feature."""
    return service.status()


# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
'''


def get_feature_service_template(class_name: str, feature_name: str):
    """Template for feature service class."""
    return f'''"""
Service layer for {feature_name}.
Encapsulates business logic and domain rules.
"""


class {class_name}Service:
    """Handles logic for the {feature_name} feature."""

    def __init__(self):
        """Initialize dependencies or configuration here."""
        pass

    def status(self) -> dict:
        """Return the operational status of this feature."""
        return {{"message": "Feature {feature_name} is ready!"}}
'''


def get_feature_entities_template(feature_name: str):
    """Template for feature entities."""
    return f'''"""
Entities for {feature_name}.
Define ORM or domain models here.
"""

# TODO: Define your entities/models here
'''


def get_feature_schemas_template(class_name: str, feature_name: str):
    """Template for feature schemas."""
    return f'''"""
Pydantic schemas for {feature_name}.
"""
from pydantic import BaseModel


class {class_name}StatusResponse(BaseModel):
    """Response schema for {feature_name} status."""
    message: str
'''


def get_feature_readme_template(class_name: str, feature_name: str):
    """Template for feature README."""
    return f'''# 🧩 Feature: {class_name}

This feature is part of the Octopus architecture.

## Overview
Describe the purpose and behavior of this feature.

## Structure
- `router.py` → HTTP routes and sub-feature mounting
- `service.py` → business logic class ({class_name}Service)
- `entities.py` → domain entities
- `schemas.py` → Pydantic schemas
- `features/` → recursive child features
- `shared/` → recursive shared utilities

Refer to `/docs` for architecture details.
'''


def get_feature_todo_template(class_name: str):
    """Template for feature TODO."""
    return f'''# TODO for {class_name}

- [ ] Implement domain logic in the service class
- [ ] Add API routes for CRUD operations
- [ ] Write unit tests
- [ ] Add integration tests
- [ ] Document API endpoints
'''


def get_shared_service_template(class_name: str, shared_name: str):
    """Template for shared service class."""
    # Special case for 'config' shared module - provide Settings class
    if shared_name == "config":
        return '''"""
Application configuration using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file=".env")
    
    app_name: str = "Octopus App"
    environment: str = "development"
    database_url: str | None = None


# Global settings instance
settings = Settings()
'''
    
    # Special case for 'routing' shared module - provide auto-discovery utility
    if shared_name == "routing":
        return '''"""
Shared routing utilities.
Provides centralized auto-discovery for feature routers.
"""
import importlib
import pkgutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter


def auto_discover_routers(
    parent_router: APIRouter,
    current_module_file: str,
    current_package: Optional[str],
    verbose: bool = False
) -> None:
    """
    Automatically discover and mount routers from sub-features.
    
    This function scans the 'features/' subdirectory relative to the calling module
    and automatically includes any routers found in sub-feature modules.
    
    Args:
        parent_router: The APIRouter instance to mount discovered routers onto
        current_module_file: Pass __file__ from the calling module
        current_package: Pass __package__ from the calling module (for relative imports)
        verbose: If True, print discovery information (useful for debugging)
    
    Example:
        from fastapi import APIRouter
        from app.shared.routing import auto_discover_routers
        
        router = APIRouter(prefix="/users", tags=["users"])
        
        # ... add your routes ...
        
        # Automatically mount sub-feature routers
        auto_discover_routers(router, __file__, __package__)
    
    This eliminates the need for manual router registration and ensures
    consistent behavior across all nesting levels.
    """
    # Resolve the features directory relative to the calling module
    current_dir = Path(current_module_file).parent
    features_path = current_dir / "features"
    
    # Only proceed if features directory exists
    if not features_path.exists():
        if verbose:
            print(f"[Routing] No features directory at: {features_path}")
        return
    
    if verbose:
        print(f"[Routing] Discovering features in: {features_path}")
    
    # Iterate through all modules in the features directory
    for _, module_name, is_pkg in pkgutil.iter_modules([str(features_path)]):
        if not is_pkg:
            # Skip non-package modules
            if verbose:
                print(f"[Routing] Skipping non-package: {module_name}")
            continue
        
        try:
            # Import the router module using relative imports
            if current_package:
                module = importlib.import_module(
                    f".features.{module_name}.router",
                    package=current_package
                )
            else:
                # Fallback for root-level imports
                module = importlib.import_module(f"features.{module_name}.router")
            
            # Check if the module has a router attribute
            if not hasattr(module, "router"):
                if verbose:
                    print(f"[Routing] Warning: {module_name}.router has no 'router' attribute")
                continue
            
            # Mount the discovered router
            parent_router.include_router(module.router)
            
            if verbose:
                print(f"[Routing] ✓ Mounted: {module_name}")
        
        except ModuleNotFoundError as e:
            if verbose:
                print(f"[Routing] Module not found: {module_name} - {e}")
        
        except AttributeError as e:
            if verbose:
                print(f"[Routing] Attribute error in {module_name}: {e}")
        
        except Exception as e:
            # Catch any other errors to prevent one bad feature from breaking all discovery
            if verbose:
                print(f"[Routing] Error loading {module_name}: {type(e).__name__}: {e}")


class RoutingService:
    """Service for routing utilities and information."""
    
    def info(self) -> dict:
        """Return information about the routing module."""
        return {
            "message": "Shared routing module is ready.",
            "provides": ["auto_discover_routers"]
        }
'''
    
    # Default template for other shared modules
    return f'''"""
Shared service for {shared_name}.
Provides reusable logic accessible across features.
"""


class {class_name}Service:
    """Utility or config service for {shared_name}."""

    def __init__(self):
        """Initialize shared resources."""
        pass

    def info(self) -> dict:
        """Return information about this shared module."""
        return {{"message": "Shared module {shared_name} is ready."}}
'''


def get_shared_entities_template(shared_name: str):
    """Template for shared entities."""
    return f'''"""
Shared entities for {shared_name}.
Define reusable ORM models or domain objects.
"""

# Example:
# from sqlalchemy import Column, Integer, String, Base
#
# class SharedExample(Base):
#     __tablename__ = "shared_example"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
'''


def get_shared_schemas_template(class_name: str, shared_name: str):
    """Template for shared schemas."""
    return f'''"""
Shared schemas for {shared_name}.
Reusable Pydantic models for features.
"""
from pydantic import BaseModel


class {class_name}InfoResponse(BaseModel):
    """Response schema for {shared_name} info."""
    message: str


# Example:
# class SharedExampleSchema(BaseModel):
#     id: int
#     name: str
'''


def get_shared_readme_template(class_name: str, shared_name: str):
    """Template for shared README."""
    return f'''# 🧩 Shared Module: {class_name}

Provides utilities, configuration, entities, and schemas shared across features.

## Usage
Features in the same Octopus app can import this module directly:
```python
from app.shared.{shared_name}.service import {class_name}Service
from app.shared.{shared_name}.entities import *
from app.shared.{shared_name}.schemas import *
```

## Structure
- `service.py` → reusable logic
- `entities.py` → ORM/domain entities
- `schemas.py` → Pydantic models
- `features/` → optional nested features
- `shared/` → optional sub-shared modules

Refer to `/docs` for architecture details.
'''


def get_shared_todo_template(class_name: str):
    """Template for shared TODO."""
    return f'''# TODO for {class_name}

- [ ] Implement shared logic in service.py
- [ ] Define common entities in entities.py
- [ ] Define shared schemas in schemas.py
- [ ] Add nested features if needed
- [ ] Write tests
'''


def get_architecture_doc_template():
    """Template for ARCHITECTURE.md documentation."""
    return '''# 🐙 Octopus Architecture Guide

## Overview

This project follows the **Octopus Recursive Fractal Architecture** - a scalable pattern where every component (app, feature, shared module) follows the same structure recursively.

## Core Principles

### 1. Fractal Structure
Every unit (app, feature, or shared module) has the same structure:
```
unit/
├── router.py       # HTTP routes (features only)
├── service.py      # Business logic
├── entities.py     # Database/ORM models
├── schemas.py      # Pydantic models for API
├── features/       # Nested sub-features
└── shared/         # Nested shared modules
```

### 2. Onion Architecture Layers

**Outer Layer → Inner Layer:**
- `router.py` → API/HTTP layer
- `service.py` → Business logic layer
- `entities.py` → Domain/Data layer
- `schemas.py` → Contracts/Validation layer

**Dependencies flow inward:** Routers use Services, Services use Entities.

### 3. Auto-Discovery Pattern
Routes are automatically mounted using Python's module inspection:
- Parent routers discover and mount child routers
- No manual registration needed
- Add a feature, it's automatically available

## File Responsibilities

### router.py
- Defines HTTP endpoints
- Handles request/response
- Uses Service classes for logic
- Auto-mounts sub-feature routers

**Example:**
```python
from fastapi import APIRouter
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])
service = UserService()

@router.get("/")
def list_users():
    return service.get_all_users()
```

### service.py
- Contains business logic
- Orchestrates operations
- Uses entities for data access
- No HTTP-specific code

**Example:**
```python
class UserService:
    def __init__(self):
        # Initialize dependencies (DB, other services)
        pass
    
    def get_all_users(self):
        # Business logic here
        return []
```

### entities.py
- Database models (SQLAlchemy/ORM)
- Domain entities
- Database schema definitions

**Example:**
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
```

### schemas.py
- Pydantic models for API validation
- Request/Response schemas
- Data transfer objects (DTOs)

**Example:**
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

## Entity vs Schema

**When to use entities.py:**
- Database table definitions
- ORM model relationships
- Database constraints
- Internal data structures

**When to use schemas.py:**
- API request validation
- API response serialization
- External data contracts
- Type safety for API layer

**Typical flow:**
1. Client sends JSON → Validated by `UserCreate` schema
2. Service creates entity → `User(name=..., email=...)`
3. Entity saved to database
4. Entity converted to schema → Returns `UserResponse`

## Features vs Shared

### Use Features when:
- Exposing HTTP endpoints
- Implementing business domains (users, products, orders)
- Building vertical slices of functionality
- Need to nest sub-features

### Use Shared when:
- Creating utilities/helpers (database, auth, logging)
- Defining common models/entities
- Building cross-cutting concerns that should be available everywhere
- Configuration and settings
- No HTTP endpoints needed

### Shared Module Cascading (Key Philosophy)

**Shared modules automatically cascade down to all nested features:**

```
app/shared/config/          # Available to ALL features at any depth
app/shared/database/        # Available to ALL features at any depth

app/features/users/
├── __init__.py            # Has: ...shared.config, ...shared.database
├── shared/validation/     # Available to users and its nested features
└── features/profile/
    └── __init__.py        # Has: ....shared.config (from app)
                           #      ....shared.database (from app)  
                           #      ...shared.validation (from parent)
```

**Benefits:**
- ✅ App-level shared modules (config, database) accessible everywhere
- ✅ Feature-level shared modules cascade to nested features
- ✅ No manual imports needed - automatically commented in `__init__.py`
- ✅ Just uncomment the imports you need

**Example imports in a nested feature:**
```python
# app/features/users/features/profile/__init__.py
"""Feature module initialization."""

# Auto-imported shared module: config
# from ....shared.config.service import *
# from ....shared.config.schemas import *

# Auto-imported shared module: database
# from ....shared.database.service import *
# from ....shared.database.schemas import *

# Auto-imported shared module: validation
# from ...shared.validation.service import *
# from ...shared.validation.schemas import *
```

## Nesting Guidelines

### Recommended Depth Limits
- **Maximum 3 levels** recommended for clarity
- Beyond 3 levels, consider if the feature hierarchy makes sense
- **Note:** With cascading shared modules, deep nesting is more viable than before

### Good Nesting Examples:
```
app/features/users/             # Level 1: User domain
├── features/profile/           # Level 2: User profile
│   └── features/avatar/        # Level 3: Profile avatar (still has access to app/shared/*)
└── features/settings/          # Level 2: User settings
```

### Why Cascading Changes the Game:
**Before:** Deep nesting meant losing access to app-level utilities
**Now:** All features inherit shared modules from parent scopes (with absolute imports)

```python
# Even at depth 3, you still have clean imports:
from app.shared.config.service import settings      # App config
from app.shared.database.service import get_db      # App database
from app.features.users.shared.user_utils import validate   # Parent's shared module

# No more confusing relative imports:
# from ......shared.config import settings  ❌ Avoid this!
```

### When to Stop Nesting:
- If relationships become unclear (not truly nested concepts)
- If features are too granular (single endpoint with no sub-features)
- If URLs become confusing (`/users/profile/avatar/settings/theme/colors`)

### Refactoring Pattern:
```
# Instead of unclear deep nesting:
app/features/ecommerce/features/products/features/reviews/features/moderation/

# Prefer flat, clear structure:
app/features/ecommerce/
app/features/product_reviews/
app/features/review_moderation/
```

**Rule of Thumb:** Nest when there's a true parent-child relationship, not just for code organization.

## Auto-Mounting Mechanism

### How It Works:

The Octopus architecture uses a **centralized auto-discovery utility** (`app.shared.routing`) to automatically mount sub-feature routers:

1. **Dynamic Path Resolution**: Uses `Path(__file__).parent` to find `features/` relative to caller
2. **Relative Imports**: Uses `__package__` for correct module resolution at any nesting level
3. **Error Handling**: Gracefully handles missing or malformed router modules
4. **Consistent Everywhere**: Same function works from root to deeply nested features

### Implementation:

Every `router.py` file ends with:
```python
from app.shared.routing import auto_discover_routers

# ... define your routes ...

# Automatically mount sub-feature routers
auto_discover_routers(router, __file__, __package__)
```

### What Gets Mounted:

The utility scans `features/` subdirectory and:
- ✅ Imports each module's `router.py`
- ✅ Mounts `router` attribute onto parent
- ✅ Preserves child's prefix/tags
- ✅ Skips modules without valid routers
- ❌ Silent failures prevented with optional verbose logging

### Example:
```python
# app/features/users/router.py
router = APIRouter(prefix="/users", tags=["users"])

# Auto-discovers: app/features/users/features/profile/router.py
# Result: /users/profile/* endpoints (prefix preserved)
```

### Benefits:

- **No Manual Registration**: Just create files, they're auto-mounted
- **AI-Friendly**: Consistent pattern at all levels
- **Bulletproof**: Works regardless of CWD or nesting depth
- **Debuggable**: Enable verbose mode to see what's being discovered

```python
# Debug mode (in development)
auto_discover_routers(router, __file__, __package__, verbose=True)
```

## Best Practices

### 1. Service Layer
- Keep services focused (Single Responsibility)
- Use dependency injection
- Handle errors at service level
- Return domain objects, not HTTP responses

### 2. Router Layer
- Thin routers (delegate to services)
- Use Pydantic schemas for validation
- Handle HTTP-specific logic only
- Use FastAPI's Depends for DI

### 3. Testing
- Test services independently
- Mock external dependencies
- Integration tests for routers
- Mirror test structure to app structure

### 4. Error Handling
```python
# In service.py
class UserService:
    def get_user(self, user_id: int):
        user = # ... fetch from DB
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

# In router.py
from fastapi import HTTPException

@router.get("/{user_id}")
def get_user(user_id: int):
    try:
        return service.get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### 5. Dependency Injection
```python
# shared/database/service.py
from sqlalchemy.orm import Session

def get_db() -> Session:
    # Database connection logic
    pass

# features/users/router.py
from fastapi import Depends
from app.shared.database.service import get_db

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return service.get_all_users(db)
```

## Common Patterns

### Pattern 1: CRUD Feature
```
features/users/
├── router.py       # GET, POST, PUT, DELETE endpoints
├── service.py      # UserService with CRUD methods
├── entities.py     # User ORM model
└── schemas.py      # UserCreate, UserUpdate, UserResponse
```

### Pattern 2: Authentication (Shared)
```
shared/auth/
├── service.py      # AuthService (no router!)
├── entities.py     # Session, Token models
└── schemas.py      # LoginRequest, TokenResponse
```

### Pattern 3: Nested Feature Domain
```
features/blog/
├── router.py               # Blog home endpoints
├── features/posts/         # Blog posts
│   ├── router.py           # CRUD for posts
│   └── features/comments/  # Post comments
└── features/authors/       # Blog authors
```

## Migration & Refactoring

### Adding a Feature to Existing Code:
1. Create feature directory in appropriate location
2. Move relevant routes to `router.py`
3. Extract business logic to `service.py`
4. Define models in `entities.py` and `schemas.py`
5. Auto-mounting handles the rest!

### Splitting a Large Feature:
1. Identify logical sub-domains
2. Create `features/` subdirectory
3. Move routes/services to sub-features
4. Update imports
5. Test auto-mounting works

## Performance Considerations

### Auto-Discovery Overhead:
- Happens once at startup
- Minimal performance impact
- Use caching for production

### Deep Nesting:
- Can increase import complexity
- Impacts cold start time
- Keep depth ≤ 3 levels

## Troubleshooting

### Routes Not Showing:
1. Check router has correct prefix
2. Verify `router` is exported in `router.py`
3. Ensure parent is importing correctly
4. Check for import errors in logs

### Circular Imports:
1. Use lazy imports in services
2. Move shared code to `shared/` modules
3. Avoid cross-feature imports (use shared instead)

## Further Reading

- `/docs/BEST_PRACTICES.md` - Coding standards
- `/docs/EXAMPLES.md` - Real-world patterns
- `/docs/TESTING.md` - Testing strategies
'''


def get_best_practices_doc_template():
    """Template for BEST_PRACTICES.md documentation."""
    return '''# 🎯 Best Practices Guide

## Code Organization

### Feature Structure
✅ **DO:**
```python
# Clear separation of concerns
features/users/
├── router.py       # HTTP layer
├── service.py      # Business logic
├── entities.py     # Data models
└── schemas.py      # API contracts
```

❌ **DON'T:**
```python
# Mixing concerns
features/users/
└── users.py        # Everything in one file
```

### Naming Conventions

#### Files
- Use `snake_case` for feature names: `user_profile`, `blog_posts`
- Standard filenames: `router.py`, `service.py`, `entities.py`, `schemas.py`

#### Classes
- Services: `{Feature}Service` → `UserService`, `BlogPostService`
- Entities: Singular nouns → `User`, `BlogPost`
- Schemas: Descriptive names → `UserCreate`, `UserResponse`

#### Functions
- Router functions: Verb + noun → `create_user()`, `list_posts()`
- Service methods: Business-focused → `authenticate()`, `publish_post()`

## Shared Modules & Cascading Imports

### Philosophy: Shared Modules Cascade Down

**Key Concept:** Shared modules at any level are automatically available to all nested features below them.

```
app/shared/config/          ← Available to ALL features
app/shared/database/        ← Available to ALL features

app/features/users/
├── __init__.py            # Auto-imports: config, database
├── shared/validation/     ← Available to users and nested features
└── features/profile/
    └── __init__.py        # Auto-imports: config, database, validation
```

### When to Create Shared Modules

#### App-Level Shared (`app/shared/`)
✅ **Use for:**
- Configuration (already created: `config/`)
- Database connections and sessions
- Authentication & authorization
- Logging utilities
- Common validators
- Email/notification services

**These are available EVERYWHERE in your app.**

#### Feature-Level Shared (`features/users/shared/`)
✅ **Use for:**
- Feature-specific utilities
- Domain-specific validators
- Feature-scoped helpers
- Only needed by this feature and its children

### Using Shared Modules

Every feature's `__init__.py` contains auto-generated import comments:

```python
# app/features/users/features/profile/__init__.py
"""Feature module initialization."""

# Auto-imported shared module: config
# from app.shared.config.service import settings
# from app.shared.config.schemas import *

# Auto-imported shared module: database
# from app.shared.database.service import get_db
# from app.shared.database.schemas import *

# Auto-imported shared module: validation  
# from app.features.users.shared.validation.service import *
# from app.features.users.shared.validation.schemas import *
```

**To use them:**
1. Uncomment the imports you need
2. Or import directly in your service/router files

```python
# In profile/service.py
from app.shared.config.service import settings
from app.shared.database.service import get_db

class ProfileService:
    def __init__(self):
        self.db_url = settings.database_url  # ✅ Works!
```

**Why absolute imports?**
- ✅ **Readable** - `app.shared.config` is clear, not `......shared.config`
- ✅ **Refactorable** - Move features without breaking imports
- ✅ **IDE-friendly** - Better autocomplete and navigation
- ✅ **Explicit** - Always know exactly where code comes from

### Benefits of Cascading

✅ **No manual wiring** - Just create the shared module, it propagates automatically  
✅ **Deep nesting viable** - Even at depth 5, you still have access to app/shared/config  
✅ **Clear dependencies** - See all available shared modules in `__init__.py`  
✅ **Opt-in usage** - Imports are commented, enable only what you need

## Service Layer Best Practices

### 1. Single Responsibility
```python
# ✅ GOOD: Focused service
class UserService:
    def create_user(self, data: UserCreate) -> User:
        # User creation logic only
        pass
    
    def update_user(self, user_id: int, data: UserUpdate) -> User:
        # User update logic only
        pass

# ❌ BAD: Too many responsibilities
class UserService:
    def create_user(self, data): pass
    def send_email(self, to): pass
    def generate_report(self): pass
    def process_payment(self): pass
```

### 2. Dependency Injection
```python
# ✅ GOOD: Injectable dependencies
class UserService:
    def __init__(self, db: Database, email_service: EmailService):
        self.db = db
        self.email_service = email_service
    
    def create_user(self, data: UserCreate) -> User:
        user = User(**data.dict())
        self.db.add(user)
        self.email_service.send_welcome(user.email)
        return user

# Usage in router
@router.post("/")
def create_user(
    data: UserCreate,
    db: Database = Depends(get_db),
    email: EmailService = Depends(get_email_service)
):
    service = UserService(db, email)
    return service.create_user(data)
```

### 3. Error Handling
```python
# ✅ GOOD: Service raises domain exceptions
class UserService:
    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

# Router translates to HTTP errors
@router.get("/{user_id}")
def get_user(user_id: int):
    try:
        return service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Router Layer Best Practices

### 1. Thin Routers
```python
# ✅ GOOD: Router delegates to service
@router.post("/")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_user(data)

# ❌ BAD: Business logic in router
@router.post("/")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    # Validation logic
    if len(data.password) < 8:
        raise HTTPException(400, "Password too short")
    
    # Business logic
    hashed = hash_password(data.password)
    user = User(name=data.name, password=hashed)
    
    # Database logic
    db.add(user)
    db.commit()
    
    # Email logic
    send_welcome_email(user.email)
    
    return user
```

### 2. Use Response Models
```python
# ✅ GOOD: Explicit response schema
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    return service.get_user(user_id)

# ❌ BAD: No type safety
@router.get("/{user_id}")
def get_user(user_id: int):
    return service.get_user(user_id)
```

### 3. Status Codes
```python
# ✅ GOOD: Explicit status codes
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate):
    return service.create_user(data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    service.delete_user(user_id)
```

## Entity Best Practices

### 1. Clear Relationships
```python
# ✅ GOOD: Well-defined relationships
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Clear relationship definition
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User", back_populates="posts")
```

### 2. Constraints & Validation
```python
# ✅ GOOD: Database-level constraints
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
```

## Schema Best Practices

### 1. Request vs Response Schemas
```python
# ✅ GOOD: Separate schemas for different use cases
class UserCreate(BaseModel):
    """Schema for creating a user."""
    name: str
    email: EmailStr
    password: str  # Password in create request

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: str | None = None
    email: EmailStr | None = None

class UserResponse(BaseModel):
    """Schema for returning user data."""
    id: int
    name: str
    email: str
    # No password in response!
    
    class Config:
        from_attributes = True  # Works with ORM models
```

### 2. Validation
```python
# ✅ GOOD: Schema-level validation
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
    
    @validator('name')
    def name_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('name cannot contain spaces')
        return v
```

## Testing Best Practices

### 1. Test Structure Mirrors App Structure
```
tests/
└── app/
    ├── features/
    │   └── users/
    │       ├── test_router.py
    │       ├── test_service.py
    │       └── test_integration.py
    └── shared/
        └── auth/
            └── test_service.py
```

### 2. Unit Test Services
```python
# ✅ GOOD: Test service independently
def test_create_user():
    # Mock dependencies
    mock_db = Mock()
    mock_email = Mock()
    
    service = UserService(mock_db, mock_email)
    user = service.create_user(UserCreate(name="Test", email="test@example.com"))
    
    assert user.name == "Test"
    mock_db.add.assert_called_once()
    mock_email.send_welcome.assert_called_once()
```

### 3. Integration Test Routers
```python
# ✅ GOOD: Test full request/response cycle
from fastapi.testclient import TestClient

def test_create_user_endpoint():
    client = TestClient(app)
    response = client.post(
        "/users/",
        json={"name": "Test", "email": "test@example.com", "password": "secret"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert "password" not in data  # Verify password not returned
```

## Database Best Practices

### 1. Connection Management
```python
# shared/database/service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Transactions
```python
# ✅ GOOD: Explicit transaction handling
class UserService:
    def create_user_with_profile(self, user_data, profile_data):
        try:
            user = User(**user_data.dict())
            self.db.add(user)
            self.db.flush()  # Get user.id without committing
            
            profile = Profile(user_id=user.id, **profile_data.dict())
            self.db.add(profile)
            
            self.db.commit()
            return user
        except Exception:
            self.db.rollback()
            raise
```

## Security Best Practices

### 1. Never Return Sensitive Data
```python
# ✅ GOOD: UserResponse excludes password
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # password field not included

# ❌ BAD: Returns everything
@router.get("/{user_id}")
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
    # Returns password hash!
```

### 2. Validate All Inputs
```python
# ✅ GOOD: Pydantic validates automatically
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    age: int = Field(ge=18)  # Must be >= 18
    website: HttpUrl | None = None  # Validates URL format
```

### 3. Use Dependencies for Auth
```python
# shared/auth/service.py
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Verify token and return user
    pass

# features/users/router.py
@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

## Performance Best Practices

### 1. Lazy Loading vs Eager Loading
```python
# ✅ GOOD: Eager load related data when needed
from sqlalchemy.orm import joinedload

def get_user_with_posts(user_id: int):
    return db.query(User)\\
        .options(joinedload(User.posts))\\
        .filter(User.id == user_id)\\
        .first()

# ❌ BAD: N+1 query problem
user = db.query(User).filter(User.id == user_id).first()
for post in user.posts:  # Triggers a query for each post!
    print(post.title)
```

### 2. Pagination
```python
# ✅ GOOD: Always paginate lists
@router.get("/", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 100):
    return service.list_users(skip=skip, limit=limit)
```

### 3. Caching
```python
# ✅ GOOD: Cache expensive operations
from functools import lru_cache

class UserService:
    @lru_cache(maxsize=128)
    def get_user_stats(self, user_id: int):
        # Expensive calculation
        return calculate_stats(user_id)
```

## Code Quality

### 1. Type Hints
```python
# ✅ GOOD: Full type hints
def create_user(self, data: UserCreate, db: Session) -> User:
    user = User(**data.dict())
    db.add(user)
    db.commit()
    return user
```

### 2. Docstrings
```python
# ✅ GOOD: Clear docstrings
class UserService:
    """Service for managing user operations.
    
    Handles user creation, updates, and authentication.
    """
    
    def create_user(self, data: UserCreate) -> User:
        """Create a new user account.
        
        Args:
            data: User creation data with name, email, and password.
            
        Returns:
            The newly created User instance.
            
        Raises:
            DuplicateEmailError: If email already exists.
        """
        pass
```

### 3. Constants
```python
# ✅ GOOD: Use constants
MAX_NAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8
DEFAULT_PAGE_SIZE = 20

class UserCreate(BaseModel):
    name: str = Field(..., max_length=MAX_NAME_LENGTH)
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)
```

## When to Refactor

### Signs It's Time to Extract a Feature:
- Single file > 500 lines
- Router has > 10 endpoints
- Service has > 10 methods
- Multiple unrelated responsibilities

### Signs It's Time to Extract Shared Module:
- Same code duplicated across 3+ features
- Utility functions scattered everywhere
- Cross-cutting concern (logging, auth, etc.)

### Signs It's Time to Stop Nesting:
- Already at depth 3
- Feature relationships unclear
- Hard to explain the hierarchy
- Circular dependency issues
'''


def get_examples_doc_template():
    """Template for EXAMPLES.md documentation."""
    return '''# 📚 Real-World Examples

## Example 1: Simple CRUD Feature

### Structure
```
features/products/
├── router.py
├── service.py
├── entities.py
└── schemas.py
```

### entities.py
```python
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
```

### schemas.py
```python
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    
    class Config:
        from_attributes = True
```

### service.py
```python
from sqlalchemy.orm import Session
from .entities import Product
from .schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, data: ProductCreate) -> Product:
        product = Product(**data.dict())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_product(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def list_products(self, skip: int = 0, limit: int = 100) -> list[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()
    
    def update_product(self, product_id: int, data: ProductUpdate) -> Product | None:
        product = self.get_product(product_id)
        if not product:
            return None
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        product = self.get_product(product_id)
        if not product:
            return False
        
        self.db.delete(product)
        self.db.commit()
        return True
```

### router.py
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.database.service import get_db
from .service import ProductService
from .schemas import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

def get_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_service)
):
    """Create a new product."""
    return service.create_product(data)

@router.get("/", response_model=list[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_service)
):
    """List all products with pagination."""
    return service.list_products(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """Get a single product by ID."""
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    service: ProductService = Depends(get_service)
):
    """Update a product."""
    product = service.update_product(product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_service)
):
    """Delete a product."""
    if not service.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
```

## Example 2: Nested Feature (Blog with Posts and Comments)

### Structure
```
features/blog/
├── router.py                   # Blog home
├── service.py
├── features/
│   ├── posts/                  # Blog posts
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── entities.py
│   │   ├── schemas.py
│   │   └── features/
│   │       └── comments/       # Post comments
│   │           ├── router.py
│   │           ├── service.py
│   │           ├── entities.py
│   │           └── schemas.py
│   └── authors/                # Blog authors
│       ├── router.py
│       ├── service.py
│       ├── entities.py
│       └── schemas.py
```

### Result URLs:
- `GET /blog/` - Blog home
- `GET /blog/posts/` - List posts
- `POST /blog/posts/` - Create post
- `GET /blog/posts/{post_id}/comments/` - List comments
- `POST /blog/posts/{post_id}/comments/` - Create comment
- `GET /blog/authors/` - List authors

## Example 3: Shared Authentication Module

### Structure
```
shared/auth/
├── service.py      # No router.py!
├── entities.py
└── schemas.py
```

### entities.py
```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### schemas.py
```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### service.py
```python
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .entities import User
from .schemas import LoginRequest, TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session, secret_key: str):
        self.db = db
        self.secret_key = secret_key
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, user_id: int, expires_delta: timedelta = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(minutes=15)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")
    
    def login(self, credentials: LoginRequest) -> TokenResponse:
        user = self.authenticate_user(credentials.email, credentials.password)
        if not user:
            raise ValueError("Invalid credentials")
        
        access_token = self.create_access_token(user.id)
        return TokenResponse(access_token=access_token)
```

### Usage in a feature:
```python
# features/users/router.py
from fastapi import Depends
from app.shared.auth.service import AuthService
from app.shared.auth.schemas import LoginRequest

@router.post("/login")
def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.login(credentials)
```

## Example 4: Database Setup (Shared Module)

### shared/database/service.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.shared.config.service import settings

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

def get_db() -> Session:
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    # Import all models here to register them
    from app.features.users.entities import User
    from app.features.products.entities import Product
    
    Base.metadata.create_all(bind=engine)
```

### Usage in main.py:
```python
from fastapi import FastAPI
from app.shared.database.service import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()
```

## Example 5: Error Handling Pattern

### shared/exceptions/service.py
```python
class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: any):
        super().__init__(
            message=f"{resource} with id {identifier} not found",
            status_code=404
        )

class DuplicateError(AppException):
    def __init__(self, resource: str, field: str, value: any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            status_code=409
        )

class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)
```

### Error handler in main.py:
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.shared.exceptions.service import AppException

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
```

### Usage in service:
```python
from app.shared.exceptions.service import NotFoundError, DuplicateError

class UserService:
    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User", user_id)
        return user
    
    def create_user(self, data: UserCreate) -> User:
        # Check for duplicate email
        existing = self.db.query(User).filter(User.email == data.email).first()
        if existing:
            raise DuplicateError("User", "email", data.email)
        
        user = User(**data.dict())
        self.db.add(user)
        self.db.commit()
        return user
```
'''


def get_test_health_template():
    """Template for health/status tests."""
    return '''"""
Health endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test that health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
'''


def get_test_conftest_template():
    """Template for pytest conftest.py with fixtures."""
    return '''"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
'''


def get_feature_test_template(class_name: str, feature_name: str):
    """Template for feature tests."""
    return f'''"""
Tests for {class_name} feature.
"""
import pytest
from fastapi.testclient import TestClient


def test_{feature_name}_endpoint(client: TestClient):
    """Test that /{feature_name} endpoint is accessible."""
    response = client.get("/{feature_name}")
    assert response.status_code in [200, 404]  # Adjust based on your implementation


def test_{feature_name}_service():
    """Test {class_name}Service methods."""
    # TODO: Add service layer tests
    pass
'''
