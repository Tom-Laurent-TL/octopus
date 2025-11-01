# Feature Implementation Guide

This guide provides step-by-step instructions for implementing new features in the FastAPI application, following the established patterns used in the `conversations` and `users` features.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Implementation Steps](#implementation-steps)
- [Code Examples](#code-examples)
- [Testing Guidelines](#testing-guidelines)
- [Best Practices](#best-practices)

## Architecture Overview

Our application follows a **feature-based architecture** with clear separation of concerns:

```
app/features/<feature_name>/
├── router.py      # HTTP layer (endpoints, request/response handling)
├── service.py     # Business logic layer (operations, validations)
└── schemas.py     # Pydantic models (data validation, serialization)

app/db/
└── models.py      # SQLAlchemy ORM models (database schema)

tests/features/<feature_name>/
├── test_router.py # HTTP endpoint tests
└── test_service.py # Business logic tests
```

### Layer Responsibilities

1. **Router Layer** (`router.py`): 
   - Handle HTTP requests/responses
   - Call service layer methods
   - Minimal logic - just orchestration
   
2. **Service Layer** (`service.py`):
   - Business logic and validation
   - Database operations
   - Should be database-aware but framework-agnostic
   
3. **Schema Layer** (`schemas.py`):
   - Data validation
   - Request/response models
   - Serialization/deserialization

4. **Model Layer** (`models.py`):
   - Database schema definition
   - Relationships between tables

## Implementation Steps

### Step 1: Define Database Model

Add your model to `app/db/models.py`:

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class YourModel(Base):
    __tablename__ = "your_table_name"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Fields
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys (if needed)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="your_models")
```

**Important:** If adding relationships, update the related model:
```python
# In the User model
your_models = relationship("YourModel", back_populates="user")
```

#### Many-to-Many Relationships

For scenarios where entities can have multiple relationships (e.g., users in conversations, students in courses):

```python
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime

# 1. Create association table (before model definitions)
your_association = Table(
    'your_association_table',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('your_model_id', Integer, ForeignKey('your_table_name.id'), primary_key=True),
    Column('created_at', DateTime, default=utcnow, nullable=False)  # Optional metadata
)

# 2. Define the model with many-to-many relationship
class YourModel(Base):
    __tablename__ = "your_table_name"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Many-to-many relationship
    users = relationship(
        "User",
        secondary=your_association,
        back_populates="your_models"
    )

# 3. Update the related model (User)
class User(Base):
    # ... existing fields ...
    
    your_models = relationship(
        "YourModel",
        secondary=your_association,
        back_populates="users"
    )
```

**Use cases:** Chat participants, course enrollments, product categories, social media tags, team memberships.

### Step 2: Create Feature Directory

```bash
mkdir app/features/your_feature
New-Item -ItemType File -Path app/features/your_feature/__init__.py
New-Item -ItemType File -Path app/features/your_feature/schemas.py
New-Item -ItemType File -Path app/features/your_feature/service.py
New-Item -ItemType File -Path app/features/your_feature/router.py
```

### Step 3: Define Schemas

Create Pydantic models in `app/features/your_feature/schemas.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Base schema with shared fields
class YourModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True

# Schema for creation (only required fields)
class YourModelCreate(YourModelBase):
    pass

# Schema for updates (all fields optional)
class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for responses (includes DB fields)
class YourModel(YourModelBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True  # Enables ORM mode

# Public schema (safe for unauthenticated users)
class YourModelPublic(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 4: Implement Service Layer

Create business logic in `app/features/your_feature/service.py`:

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db import models

class YourFeatureService:
    """Service layer for your feature operations."""
    
    @staticmethod
    def create(
        db: Session,
        name: str,
        description: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> models.YourModel:
        """Create a new record."""
        item = models.YourModel(
            name=name,
            description=description,
            user_id=user_id
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def get(db: Session, item_id: int) -> Optional[models.YourModel]:
        """Get a record by ID."""
        return db.query(models.YourModel).filter(
            models.YourModel.id == item_id
        ).first()
    
    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List[models.YourModel]:
        """List records with optional filtering."""
        query = db.query(models.YourModel)
        
        if user_id is not None:
            query = query.filter(models.YourModel.user_id == user_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session,
        item_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[models.YourModel]:
        """Update a record."""
        item = YourFeatureService.get(db, item_id)
        if not item:
            return None
        
        if name is not None:
            item.name = name
        if description is not None:
            item.description = description
        if is_active is not None:
            item.is_active = is_active
        
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def delete(db: Session, item_id: int) -> bool:
        """Delete a record."""
        item = YourFeatureService.get(db, item_id)
        if not item:
            return False
        
        db.delete(item)
        db.commit()
        return True
```

### Step 5: Create Router

Implement HTTP endpoints in `app/features/your_feature/router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import verify_api_key
from app.features.your_feature import schemas
from app.features.your_feature.service import YourFeatureService

router = APIRouter(prefix="/your-feature", tags=["Your Feature"])

# Public endpoint (no authentication)
@router.get("/{item_id}/public", response_model=schemas.YourModelPublic)
def get_item_public(item_id: int, db: Session = Depends(get_db)):
    """Get an item (public endpoint)."""
    item = YourFeatureService.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Protected endpoint (requires authentication)
@router.post(
    "/",
    response_model=schemas.YourModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)]
)
def create_item(
    item_data: schemas.YourModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new item."""
    item = YourFeatureService.create(
        db,
        name=item_data.name,
        description=item_data.description
    )
    return item

@router.get(
    "/",
    response_model=List[schemas.YourModel],
    dependencies=[Depends(verify_api_key)]
)
def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all items."""
    return YourFeatureService.list(db, skip=skip, limit=limit)

@router.get(
    "/{item_id}",
    response_model=schemas.YourModel,
    dependencies=[Depends(verify_api_key)]
)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get an item by ID."""
    item = YourFeatureService.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put(
    "/{item_id}",
    response_model=schemas.YourModel,
    dependencies=[Depends(verify_api_key)]
)
def update_item(
    item_id: int,
    item_data: schemas.YourModelUpdate,
    db: Session = Depends(get_db)
):
    """Update an item."""
    item = YourFeatureService.update(
        db,
        item_id,
        name=item_data.name,
        description=item_data.description,
        is_active=item_data.is_active
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)]
)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item."""
    success = YourFeatureService.delete(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
```

### Step 6: Register Router

Add your router to `app/api/v1/router.py`:

```python
from app.features.your_feature.router import router as your_feature_router

# Include in the main router
api_router.include_router(your_feature_router)
```

### Step 7: Create Tests

#### Router Tests (`tests/features/your_feature/test_router.py`):

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_item(client: TestClient, auth_headers: dict):
    """Test creating a new item."""
    response = client.post(
        "/api/v1/your-feature/",
        json={
            "name": "Test Item",
            "description": "Test description"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data

def test_create_item_without_auth(client: TestClient):
    """Test that creating requires authentication."""
    response = client.post(
        "/api/v1/your-feature/",
        json={"name": "Test"}
    )
    assert response.status_code == 403

def test_list_items(client: TestClient, auth_headers: dict, test_db: Session):
    """Test listing items."""
    # Create test data
    client.post(
        "/api/v1/your-feature/",
        json={"name": "Item 1"},
        headers=auth_headers
    )
    client.post(
        "/api/v1/your-feature/",
        json={"name": "Item 2"},
        headers=auth_headers
    )
    
    # List items
    response = client.get("/api/v1/your-feature/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_get_item(client: TestClient, auth_headers: dict):
    """Test getting an item by ID."""
    # Create item
    create_response = client.post(
        "/api/v1/your-feature/",
        json={"name": "Test Item"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    # Get item
    response = client.get(
        f"/api/v1/your-feature/{item_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"

def test_get_nonexistent_item(client: TestClient, auth_headers: dict):
    """Test getting a non-existent item."""
    response = client.get(
        "/api/v1/your-feature/99999",
        headers=auth_headers
    )
    assert response.status_code == 404

def test_update_item(client: TestClient, auth_headers: dict):
    """Test updating an item."""
    # Create item
    create_response = client.post(
        "/api/v1/your-feature/",
        json={"name": "Original Name"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    # Update item
    response = client.put(
        f"/api/v1/your-feature/{item_id}",
        json={"name": "Updated Name"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

def test_delete_item(client: TestClient, auth_headers: dict):
    """Test deleting an item."""
    # Create item
    create_response = client.post(
        "/api/v1/your-feature/",
        json={"name": "To Delete"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    # Delete item
    response = client.delete(
        f"/api/v1/your-feature/{item_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(
        f"/api/v1/your-feature/{item_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404
```

#### Service Tests (`tests/features/your_feature/test_service.py`):

```python
import pytest
from sqlalchemy.orm import Session
from app.features.your_feature.service import YourFeatureService

def test_create_item_service(test_db: Session):
    """Test creating an item via service."""
    item = YourFeatureService.create(
        test_db,
        name="Test Item",
        description="Test description"
    )
    assert item.id is not None
    assert item.name == "Test Item"

def test_get_item_service(test_db: Session):
    """Test getting an item via service."""
    # Create
    created = YourFeatureService.create(test_db, name="Test")
    
    # Get
    retrieved = YourFeatureService.get(test_db, created.id)
    assert retrieved is not None
    assert retrieved.id == created.id

def test_get_nonexistent_item_service(test_db: Session):
    """Test getting a non-existent item."""
    item = YourFeatureService.get(test_db, 99999)
    assert item is None

def test_list_items_service(test_db: Session):
    """Test listing items."""
    # Create multiple items
    YourFeatureService.create(test_db, name="Item 1")
    YourFeatureService.create(test_db, name="Item 2")
    
    # List
    items = YourFeatureService.list(test_db)
    assert len(items) >= 2

def test_update_item_service(test_db: Session):
    """Test updating an item."""
    # Create
    item = YourFeatureService.create(test_db, name="Original")
    
    # Update
    updated = YourFeatureService.update(
        test_db,
        item.id,
        name="Updated"
    )
    assert updated.name == "Updated"

def test_delete_item_service(test_db: Session):
    """Test deleting an item."""
    # Create
    item = YourFeatureService.create(test_db, name="To Delete")
    
    # Delete
    success = YourFeatureService.delete(test_db, item.id)
    assert success is True
    
    # Verify deletion
    deleted = YourFeatureService.get(test_db, item.id)
    assert deleted is None
```

### Step 8: Run Tests

```bash
# Run all tests
uv run pytest -v

# Run only your feature tests
uv run pytest tests/features/your_feature/ -v

# Run with coverage
uv run pytest --cov=app/features/your_feature tests/features/your_feature/
```

## Best Practices

### 1. Separation of Concerns
- **Router**: Only handle HTTP concerns (status codes, headers, exceptions)
- **Service**: All business logic and database operations
- **Never** write database queries in routers

### 2. Error Handling
```python
# In Router
if not item:
    raise HTTPException(status_code=404, detail="Item not found")

# In Service
# Return None for not found, let router handle HTTP error
return None
```

### 3. Authentication
```python
# Protected endpoint - requires API key
@router.get("/", dependencies=[Depends(verify_api_key)])

# Public endpoint - no authentication
@router.get("/public")
```

### 4. Response Models
- Use specific schemas for responses (`response_model=schemas.YourModel`)
- Create public schemas for unauthenticated endpoints
- Never expose sensitive data in public endpoints

### 5. Validation
```python
# Use Pydantic for validation
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
```

### 6. Testing Strategy
- Test **both** router and service layers
- Router tests: HTTP behavior (status codes, auth, serialization)
- Service tests: Business logic, database operations
- Aim for >80% code coverage

### 7. Database Sessions
```python
# Always use dependency injection for DB sessions
def endpoint(db: Session = Depends(get_db)):
    # Use db here
    pass
```

### 8. Naming Conventions
- Models: `YourModel` (singular, PascalCase)
- Tables: `your_models` (plural, snake_case)
- Routers: `router` (lowercase)
- Services: `YourFeatureService` (PascalCase)
- Endpoints: Use RESTful conventions (GET, POST, PUT, DELETE)

## Common Patterns

### Pagination
```python
@router.get("/")
def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return YourService.list(db, skip=skip, limit=limit)
```

### Filtering
```python
@staticmethod
def list(
    db: Session,
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[models.YourModel]:
    query = db.query(models.YourModel)
    
    if user_id is not None:
        query = query.filter(models.YourModel.user_id == user_id)
    if is_active is not None:
        query = query.filter(models.YourModel.is_active == is_active)
    
    return query.all()
```

### Relationships
```python
# In service - eager load relationships
def get_with_relations(db: Session, item_id: int):
    return db.query(models.YourModel)\
        .filter(models.YourModel.id == item_id)\
        .options(joinedload(models.YourModel.related_items))\
        .first()
```

### Cascade Deletes
```python
# In model
related_items = relationship(
    "RelatedModel",
    back_populates="parent",
    cascade="all, delete-orphan"  # Auto-delete children
)
```

## Checklist

Before considering a feature complete:

- [ ] Database model created with proper fields and relationships
- [ ] Related models updated with back-references
- [ ] Schemas created (Create, Update, Response, Public if needed)
- [ ] Service layer with CRUD operations implemented
- [ ] Router with endpoints implemented
- [ ] Router registered in `app/api/v1/router.py`
- [ ] Router tests created (minimum 7-10 tests)
- [ ] Service tests created (minimum 5-8 tests)
- [ ] All tests passing (`uv run pytest -v`)
- [ ] Authentication applied correctly (public vs protected)
- [ ] Error handling implemented
- [ ] Documentation updated (if needed)

## Example Features

Refer to existing features for examples:

### Production Features
- **Full Feature with Service Layer**: `app/features/conversations/`
  - Complete CRUD with service layer
  - Message relationships
  - Comprehensive tests (router + service)
  
- **Authentication & Password Hashing**: `app/features/users/`
  - User registration and management
  - Password hashing with bcrypt
  - Public vs protected endpoints
  - Comprehensive tests

### Demo Features (FastAPI Tutorial Code)
- **Simple Router**: `app/features/items/`
  - Basic CRUD example
  - No service layer or schemas
  - **Note:** Demo/placeholder code - can be removed or used as simple example
  
- **Protected Endpoint**: `app/features/admin/`
  - Example of protected route
  - **Note:** Demo/placeholder code - can be removed or replaced with actual admin feature

**Recommendation:** Study `conversations/` and `users/` features as they follow the full pattern we recommend. The `items/` and `admin/` features are kept as simple examples but don't follow the complete service layer pattern.

## Troubleshooting

### Common Issues

1. **Import Errors**: Check circular imports, use `from app.db import models`
2. **Test Failures**: Ensure test database is isolated (`test_db` fixture)
3. **Authentication Issues**: Check `dependencies=[Depends(verify_api_key)]`
4. **Relationship Errors**: Verify `back_populates` is set on both models
5. **Migration Issues**: Recreate database after model changes (SQLite: delete .db file)

## Next Steps

After implementing your feature:
1. Test manually using FastAPI docs at `http://localhost:8000/docs`
2. Run full test suite: `uv run pytest -v`
3. Check coverage: `uv run pytest --cov=app --cov-report=html`
4. Update project documentation if needed
