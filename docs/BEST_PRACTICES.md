# Best Practices & Lessons Learned

This document captures real-world mistakes, iterations, and solutions encountered while building this FastAPI application. Learn from these experiences to avoid common pitfalls.

## Table of Contents
- [Dependency Management](#dependency-management)
- [Database Design](#database-design)
- [Authentication & Security](#authentication--security)
- [Password Hashing](#password-hashing)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Service Layer Pattern](#service-layer-pattern)
- [Error Handling](#error-handling)
- [Development Workflow](#development-workflow)

---

## Dependency Management

### ❌ Mistake: Using Incompatible Library Versions

**What Happened:**
- Initially used `passlib[bcrypt]>=1.7.4` for password hashing
- Passlib had compatibility issues with newer `bcrypt` versions (5.0.0+)
- Got cryptic errors: `AttributeError: module 'bcrypt' has no attribute '__about__'`
- Error message about password length limit was misleading

**The Problem:**
```toml
dependencies = [
    "passlib[bcrypt]>=1.7.4",  # ❌ Compatibility issues
]
```

**The Solution:**
```toml
dependencies = [
    "bcrypt>=4.0.0",  # ✅ Use bcrypt directly
]
```

**Implementation:**
```python
# ❌ Old approach with passlib
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)

# ✅ New approach with bcrypt directly
import bcrypt
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)
hashed_str = hashed.decode('utf-8')
```

### ✅ Best Practice: Keep Dependencies Minimal

**Guidelines:**
1. Use direct dependencies when possible (avoid unnecessary wrappers)
2. Pin major versions but allow minor/patch updates: `bcrypt>=4.0.0`
3. Test after updating dependencies: `uv sync && uv run pytest`
4. When you see compatibility errors, check if you can use the underlying library directly

**Always remember:**
```bash
# After changing dependencies
uv sync
uv sync --extra test  # Don't forget test dependencies!
uv run pytest -v     # Verify everything works
```

---

## Database Design

### ❌ Mistake: Not Planning Relationships Upfront

**What Happened:**
- Created `User` model later in the project
- Had to add `user_id` foreign key to existing `Conversation` model
- Risked breaking existing tests and data

**The Problem:**
```python
# Original Conversation model - missing user relationship
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    # No user_id! ❌
```

**The Solution:**
```python
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # ✅ Added later with nullable=True
    
    user = relationship("User", back_populates="conversations")
```

### ✅ Best Practice: Design Database Schema First

**Before writing any code:**

1. **Sketch your data model** - Identify all entities and relationships
2. **Plan foreign keys** - Consider which tables need to reference others
3. **Think about cascades** - What happens when parent records are deleted?
4. **Make strategic nullable decisions**:
   - `nullable=True` for optional relationships or backward compatibility
   - `nullable=False` for required data (new projects only)

**Example Planning Template:**
```
Entities:
- User (id, email, username, password)
- Conversation (id, title, user_id FK)
- Message (id, content, role, conversation_id FK)

Relationships:
- User -> Conversations (one-to-many)
- Conversation -> Messages (one-to-many, cascade delete)

Cascades:
- Delete User: Keep conversations (user_id becomes NULL)
- Delete Conversation: Delete all messages
```

### ❌ Mistake: Forgetting Back-Populates

**The Problem:**
```python
# In User model
conversations = relationship("Conversation")  # ❌ No back_populates

# In Conversation model  
user = relationship("User")  # ❌ No back_populates
```

**The Solution:**
```python
# In User model
conversations = relationship("Conversation", back_populates="user")  # ✅

# In Conversation model
user = relationship("User", back_populates="conversations")  # ✅
```

**Why it matters:** Without `back_populates`, SQLAlchemy doesn't maintain bidirectional relationships, leading to weird bugs and unexpected query results.

### ✅ Best Practice: Many-to-Many Relationships

**When to use:** When entities can be related to multiple instances of each other (e.g., users in conversations, students in courses, tags on posts).

**Implementation:**
```python
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime

# 1. Create association table
conversation_participants = Table(
    'conversation_participants',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('conversation_id', Integer, ForeignKey('conversations.id'), primary_key=True),
    Column('joined_at', DateTime, default=utcnow, nullable=False)  # Optional metadata
)

# 2. Define relationships in both models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # ... other fields
    
    conversations = relationship(
        "Conversation",
        secondary=conversation_participants,
        back_populates="participants"
    )

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    # ... other fields
    
    participants = relationship(
        "User",
        secondary=conversation_participants,
        back_populates="conversations"
    )
```

**Service layer operations:**
```python
class ConversationService:
    @staticmethod
    def create_conversation(db: Session, title: str, participant_ids: List[int]):
        """Create conversation with multiple participants."""
        conversation = models.Conversation(title=title)
        
        # Add participants
        users = db.query(models.User).filter(models.User.id.in_(participant_ids)).all()
        conversation.participants.extend(users)
        
        db.add(conversation)
        db.commit()
        return conversation
    
    @staticmethod
    def add_participant(db: Session, conversation_id: int, user_id: int):
        """Add user to existing conversation."""
        conversation = db.query(models.Conversation).get(conversation_id)
        user = db.query(models.User).get(user_id)
        
        if user not in conversation.participants:
            conversation.participants.append(user)
            db.commit()
        
        return conversation
    
    @staticmethod
    def list_user_conversations(db: Session, user_id: int):
        """Get all conversations for a user."""
        user = db.query(models.User).get(user_id)
        return user.conversations if user else []
```

**Schema design:**
```python
class UserInfo(BaseModel):
    """Minimal user info for nested display."""
    id: int
    username: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    participant_ids: List[int] = []  # User IDs to add

class Conversation(BaseModel):
    id: int
    title: Optional[str]
    participants: List[UserInfo] = []  # Include participant info
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

**Benefits:**
- Flexible: Supports 1-on-1, group conversations, or any number of participants
- Scalable: Easy to add metadata to the association (joined_at, role, etc.)
- Clean queries: SQLAlchemy handles the joins automatically
- Intuitive: `user.conversations` and `conversation.participants` work naturally

**Common use cases:**
- Chat applications (users ↔ conversations)
- E-commerce (orders ↔ products)
- Social media (users ↔ tags, posts ↔ categories)
- Course management (students ↔ courses)

### ✅ Best Practice: Track Related Entity Information

**For features like chat/messages, track who created what:**

```python
class Message(Base):
    """Message model with sender tracking."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who sent it
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")  # Sender information
```

**Why nullable?**
- System messages (no user)
- Bot/AI responses (no human user)
- Backward compatibility (existing messages without user_id)

**Validate in router:**
```python
@router.post("/{conversation_id}/messages")
def add_message(conversation_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    conversation = ConversationService.get_conversation(db, conversation_id)
    
    # If user_id provided, verify they're a participant
    if message.user_id:
        user_ids = [p.id for p in conversation.participants]
        if message.user_id not in user_ids:
            raise HTTPException(
                status_code=403, 
                detail="User is not a participant in this conversation"
            )
    
    return MessageService.add_message(
        db, conversation_id, message.role, message.content, message.user_id
    )
```

**Include in responses:**
```python
class Message(BaseModel):
    id: int
    conversation_id: int
    user_id: Optional[int] = None
    user: Optional[UserInfo] = None  # Nested user info
    role: str
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

**Benefits:**
- Audit trail: Know who said what
- Security: Validate participants before accepting messages
- Rich UI: Display sender name/avatar in chat interfaces
- Analytics: Track user engagement and activity

---

## Authentication & Security

### ❌ Mistake: Overcomplicated Authentication System

**What Happened:**
- Started with FastAPI tutorial code that had multiple token types
- Had `get_query_token()`, `get_token_header()`, OAuth2-style tokens
- Unnecessarily complex for a simple API

**The Problem:**
```python
# ❌ Too many authentication methods
async def get_query_token(token: str = Query(...)):
    if token != settings.query_token:
        raise HTTPException(...)

async def get_token_header(token: str = Header(...)):
    if token != settings.header_token:
        raise HTTPException(...)
```

**The Solution:**
```python
# ✅ Single, simple API key authentication
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
```

### ✅ Best Practice: Start Simple, Add Complexity When Needed

**Authentication Evolution:**

**Phase 1: API Key (Start here)**
```python
# Simple header-based authentication
X-API-Key: your-secret-key

# In code
dependencies=[Depends(verify_api_key)]
```

**Phase 2: JWT Tokens (When you need user-specific auth)**
```python
# Only add when you need:
# - User sessions
# - Token expiration
# - Role-based access
```

**Phase 3: OAuth2 (When you need third-party login)**
```python
# Only add when integrating:
# - Google/GitHub login
# - Enterprise SSO
```

**Rule of thumb:** Don't implement Phase 2 until Phase 1 is limiting you. Don't implement Phase 3 until Phase 2 is limiting you.

### ✅ Best Practice: Public vs Protected Endpoints

**Clear separation:**
```python
# Public endpoints (no auth needed)
@router.post("/users/", response_model=schemas.User)  # Registration
@router.get("/users/username/{username}", response_model=schemas.UserPublic)  # Lookup

# Protected endpoints (auth required)
@router.get("/users/", dependencies=[Depends(verify_api_key)])  # List all
@router.get("/users/{user_id}", dependencies=[Depends(verify_api_key)])  # Get by ID
@router.put("/users/{user_id}", dependencies=[Depends(verify_api_key)])  # Update
@router.delete("/users/{user_id}", dependencies=[Depends(verify_api_key)])  # Delete
```

**Guidelines:**
- **Public**: Registration, login, public profiles, health checks
- **Protected**: CRUD operations, user data, admin functions
- **Never expose sensitive data** in public endpoints (use separate schemas)

---

## Password Hashing

### ❌ Mistake: Not Handling Password Encoding

**What Happened:**
- Bcrypt requires bytes, not strings
- Forgot to encode/decode properly
- Got confusing type errors

**The Problem:**
```python
# ❌ Wrong - bcrypt needs bytes
hashed = bcrypt.hashpw(password, salt)  # TypeError!
```

**The Solution:**
```python
# ✅ Always encode/decode properly
@staticmethod
def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')  # String to bytes
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')  # Bytes back to string for DB

@staticmethod
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
```

### ✅ Best Practice: Centralize Password Operations

**Create a service method:**
```python
class UserService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for storage."""
        # Implementation here
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        # Implementation here
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        return user
```

**Benefits:**
- Single place to update hashing algorithm
- Consistent password handling
- Easy to test
- Easy to add features (password strength, history, etc.)

---

## Project Structure

### ❌ Mistake: Type-Based Organization

**What Happened:**
- Started with FastAPI tutorial structure
- Files organized by type (routers/, models/, schemas/)
- Hard to find related code as project grew

**The Problem:**
```
app/
├── routers/        # All routers mixed together
│   ├── items.py
│   ├── users.py
│   └── conversations.py
├── models/         # All models mixed together
│   └── database.py
└── schemas/        # All schemas mixed together
    └── items.py
```

**Finding code required:**
1. Open `routers/users.py`
2. Open `schemas/users.py`
3. Open `models/database.py`
4. Search for User model
5. Lose track of what you were doing 😵

### ✅ Best Practice: Feature-Based Organization

**The Solution:**
```
app/
├── core/              # Shared config and utilities
│   ├── config.py
│   └── security.py
├── db/                # Database setup and models
│   ├── database.py
│   └── models.py
└── features/          # Feature modules
    ├── conversations/
    │   ├── router.py
    │   ├── service.py
    │   └── schemas.py
    ├── users/
    │   ├── router.py
    │   ├── service.py
    │   └── schemas.py
    ├── items/         # Demo code from FastAPI tutorial
    │   └── router.py
    └── admin/         # Demo code from FastAPI tutorial
        └── router.py
```

**Benefits:**
- Everything for a feature in one place
- Easy to find related code
- Easy to delete a feature (just remove the folder)
- Better for team collaboration (less merge conflicts)
- Scales to large projects

**Note:** The `items/` and `admin/` features are placeholder code from the FastAPI tutorial. They serve as examples but can be removed or replaced with your own features.

**Mirror in tests:**
```
tests/
└── features/
    ├── conversations/
    │   ├── test_router.py
    │   └── test_service.py
    └── users/
        ├── test_router.py
        └── test_service.py
```

---

## Testing

### ❌ Mistake: Not Mirroring App Structure in Tests

**What Happened:**
- Tests in flat structure didn't match app organization
- Hard to find which tests covered which features
- Tests for deleted features left behind

**The Problem:**
```
tests/
├── test_items.py       # Which feature is this?
├── test_endpoints.py   # Tests for everything?
└── test_database.py    # Integration or unit?
```

### ✅ Best Practice: Mirror App Structure

**The Solution:**
```
tests/
├── api/
│   └── v1/
│       └── test_endpoints.py  # Integration tests for API
├── features/
│   ├── conversations/
│   │   ├── test_router.py     # HTTP layer tests
│   │   └── test_service.py    # Business logic tests
│   └── users/
│       ├── test_router.py
│       └── test_service.py
└── db/
    └── test_models.py          # Database model tests
```

**Benefits:**
- Clear test ownership
- Easy to find tests for a feature
- Easy to ensure coverage
- Delete feature = delete test folder

### ❌ Mistake: Testing Without Auth When Auth Is Required

**What Happened:**
- Created tests that passed without authentication
- Found out in production that endpoints were unprotected
- Had to retrofit auth to existing tests

**The Problem:**
```python
# ❌ Test passes but endpoint should require auth!
def test_list_users(client: TestClient):
    response = client.get("/api/v1/users/")
    assert response.status_code == 200  # Should be 403!
```

**The Solution:**
```python
# ✅ Properly test authentication requirements
def test_list_users_requires_auth(client: TestClient):
    """Test that listing users requires authentication."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 403

def test_list_users(client: TestClient, auth_headers: dict):
    """Test listing users with authentication."""
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == 200
```

### ✅ Best Practice: Test Authentication Explicitly

**For every protected endpoint:**
1. Test without auth (should fail)
2. Test with invalid auth (should fail)
3. Test with valid auth (should succeed)

**Use fixtures:**
```python
# In conftest.py
@pytest.fixture
def auth_headers(settings):
    """Provide valid authentication headers."""
    return {"X-API-Key": settings.api_key}

@pytest.fixture
def invalid_auth_headers():
    """Provide invalid authentication headers."""
    return {"X-API-Key": "invalid-key"}
```

### ❌ Mistake: Not Isolating Test Database

**What Happened:**
- Tests modified the main database
- Test data polluted development environment
- Flaky tests that passed/failed based on previous runs

**The Solution:**
```python
# In conftest.py
@pytest.fixture
def test_db():
    """Create a test database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",  # ✅ In-memory database
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

**Benefits:**
- Each test starts with clean database
- Tests don't affect each other
- Fast (in-memory)
- Can run tests in parallel

---

## Service Layer Pattern

### ❌ Mistake: Database Queries in Routers

**What Happened:**
- Started writing database queries directly in router functions
- Hard to test business logic separately
- Couldn't reuse logic across endpoints

**The Problem:**
```python
# ❌ Database logic mixed with HTTP logic
@router.post("/conversations/")
def create_conversation(
    title: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    # Business logic in router! ❌
    conversation = db.query(Conversation).filter(
        Conversation.title == title
    ).first()
    
    if conversation:
        raise HTTPException(400, "Already exists")
    
    new_conv = Conversation(title=title)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv
```

### ✅ Best Practice: Separate Service Layer

**The Solution:**
```python
# service.py - Business logic
class ConversationService:
    @staticmethod
    def create_conversation(db: Session, title: str) -> models.Conversation:
        """Create a new conversation."""
        conversation = models.Conversation(title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

# router.py - HTTP logic
@router.post("/", response_model=schemas.Conversation)
def create_conversation(
    data: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new conversation."""
    return ConversationService.create_conversation(db, data.title)
```

**Layer Responsibilities:**

| Layer | Responsibility | Never |
|-------|---------------|-------|
| Router | HTTP request/response, status codes, auth | Database queries, business logic |
| Service | Business logic, validation, database ops | HTTP concerns, status codes |
| Schema | Data validation, serialization | Business logic, database access |
| Model | Database schema, relationships | Business logic, validation |

### ✅ Best Practice: Service Layer Testing

**Test service layer independently:**
```python
def test_create_conversation_service(test_db: Session):
    """Test service layer directly (no HTTP)."""
    conv = ConversationService.create_conversation(
        test_db,
        title="Test"
    )
    assert conv.id is not None
    assert conv.title == "Test"
```

**Benefits:**
- Faster tests (no HTTP overhead)
- Test business logic directly
- Easy to mock dependencies
- Reusable across different interfaces (HTTP, CLI, queue workers)

---

## Router Best Practices

### ❌ Mistake: Wrong Route Order

**What Happened:**
- Created route `/user/{user_id}` to list user's conversations
- Placed it after `/{conversation_id}` generic route
- FastAPI matched "user" as a conversation_id, causing parsing errors

**The Problem:**
```python
# ❌ Wrong order - generic route first
@router.get("/{conversation_id}")  # This matches first!
def get_conversation(conversation_id: int):
    ...

@router.get("/user/{user_id}")  # Never reached!
def list_user_conversations(user_id: int):
    ...

# Request to /conversations/user/123
# FastAPI tries to parse "user" as conversation_id integer → Error!
```

**The Solution:**
```python
# ✅ Correct order - specific routes first
@router.get("/user/{user_id}")  # Specific route first
def list_user_conversations(user_id: int):
    ...

@router.get("/{conversation_id}")  # Generic route last
def get_conversation(conversation_id: int):
    ...
```

### ✅ Best Practice: Route Ordering Rules

**FastAPI matches routes in order of definition:**

1. **Static paths first** (exact matches)
   ```python
   @router.get("/me")  # Most specific
   @router.get("/public")
   ```

2. **Parameterized paths with prefixes** (partial matches)
   ```python
   @router.get("/user/{user_id}")
   @router.get("/conversation/{conv_id}")
   ```

3. **Generic parameterized paths last** (catch-all)
   ```python
   @router.get("/{id}")  # Least specific
   ```

**Example of correct ordering:**
```python
# ✅ Good route organization
@router.get("/")                          # 1. List all
@router.get("/me")                        # 2. Current user (static)
@router.get("/public")                    # 3. Public items (static)
@router.get("/user/{user_id}")           # 4. Specific prefix
@router.get("/search/{query}")           # 5. Specific prefix
@router.get("/{id}")                     # 6. Generic catch-all
```

**Rule of thumb:** If you get unexpected 422 validation errors on path parameters, check your route order!

---

## Error Handling

### ❌ Mistake: Inconsistent Error Responses

**The Problem:**
```python
# ❌ Inconsistent error handling
@router.get("/{id}")
def get_item(id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        return {"error": "not found"}  # ❌ Wrong status code!
    return item
```

### ✅ Best Practice: Consistent HTTP Error Handling

**The Solution:**
```python
# ✅ Proper HTTP exceptions
from fastapi import HTTPException, status

@router.get("/{id}", response_model=schemas.Item)
def get_item(id: int, db: Session = Depends(get_db)):
    item = ItemService.get(db, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
```

**Standard Error Patterns:**
```python
# 400 Bad Request - Invalid input
raise HTTPException(status_code=400, detail="Invalid email format")

# 401 Unauthorized - Missing/invalid auth
raise HTTPException(status_code=401, detail="Authentication required")

# 403 Forbidden - Valid auth but insufficient permissions
raise HTTPException(status_code=403, detail="Invalid API key")

# 404 Not Found - Resource doesn't exist
raise HTTPException(status_code=404, detail="User not found")

# 409 Conflict - Resource already exists
raise HTTPException(status_code=409, detail="Email already registered")

# 422 Unprocessable Entity - Pydantic handles this automatically
# (validation errors)
```

### ✅ Best Practice: Service Returns None, Router Handles Errors

**Pattern:**
```python
# Service - returns None for not found
class ItemService:
    @staticmethod
    def get(db: Session, item_id: int) -> Optional[models.Item]:
        return db.query(models.Item).filter(
            models.Item.id == item_id
        ).first()  # Returns None if not found

# Router - converts None to HTTP 404
@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = ItemService.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

**Why?**
- Service layer is framework-agnostic (can use in CLI, queue workers)
- Router layer handles HTTP concerns
- Clear separation of responsibilities

---

## Development Workflow

### ✅ Best Practice: Development Cycle

**The workflow that works:**

```bash
# 1. Make code changes
# ... edit files ...

# 2. Run tests frequently
uv run pytest -v

# 3. Run specific tests during development
uv run pytest tests/features/users/test_router.py -v

# 4. Check a single test
uv run pytest tests/features/users/test_router.py::test_create_user -v

# 5. Before committing - run everything
uv run pytest -v

# 6. Check coverage
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### ✅ Best Practice: Git Workflow

**Protect your work:**

```bash
# Never work directly on main
git checkout -b feature/new-feature

# Commit frequently with clear messages
git add app/features/users/
git commit -m "Add user registration endpoint"

# Test before pushing
uv run pytest -v

# Push and create PR
git push origin feature/new-feature
```

### ✅ Best Practice: Debugging Failed Tests

**When a test fails:**

1. **Read the error message** (really read it)
   ```
   ValueError: password cannot be longer than 72 bytes
   ```

2. **Check what changed** since tests last passed
   ```bash
   git diff
   ```

3. **Run just that test** with verbose output
   ```bash
   uv run pytest tests/features/users/test_router.py::test_create_user -vv
   ```

4. **Add print statements** (temporary debugging)
   ```python
   print(f"DEBUG: {variable}")
   ```

5. **Check dependencies** if error mentions a library
   ```bash
   uv pip list | grep bcrypt
   ```

6. **Try fixing in isolation** - comment out other tests
   ```python
   # @pytest.mark.skip  # Temporary
   # def test_other_thing():
   ```

---

## Key Takeaways

### 🎯 Start Simple

1. **Don't over-engineer** - Start with simple solutions
2. **Add complexity only when needed** - You aren't gonna need it (YAGNI)
3. **Follow existing patterns** - Consistency > cleverness

### 🏗️ Structure Matters

1. **Feature-based structure** - Group related code together
2. **Service layer** - Separate business logic from HTTP concerns
3. **Mirror test structure** - Tests should match app structure

### 🧪 Test Everything

1. **Test both layers** - Router tests + Service tests
2. **Test authentication** - Explicitly test auth requirements
3. **Isolate tests** - Use in-memory database
4. **Run tests frequently** - After every change

### 📦 Dependencies

1. **Keep it minimal** - Fewer dependencies = fewer problems
2. **Use direct libraries** - Avoid unnecessary wrappers
3. **Test after updates** - Always run tests after changing dependencies
4. **Check compatibility** - Read changelogs before upgrading

### 🔒 Security

1. **Start with API keys** - Simple is secure
2. **Separate public/protected** - Clear distinction in routers
3. **Never expose sensitive data** - Use public schemas
4. **Centralize auth logic** - Single source of truth

### 🐛 When Things Break

1. **Read error messages carefully** - They usually tell you what's wrong
2. **Check what changed** - Use git diff
3. **Isolate the problem** - Test one thing at a time
4. **Google is your friend** - Someone has had this problem before
5. **Simplify** - Sometimes starting over is faster

---

## Quick Reference

### Common Commands

**Development:**
```bash
# Install dependencies
uv sync
uv sync --extra test

# Run tests
uv run pytest -v                                    # All tests
uv run pytest tests/features/users/ -v              # One feature
uv run pytest tests/features/users/test_router.py::test_create_user -v  # One test

# Coverage
uv run pytest --cov=app --cov-report=html

# Run dev server
uv run fastapi dev app/main.py

# Format code (if using)
uv run black app/ tests/
uv run isort app/ tests/
```

**Testing API (Linux/Mac/WSL):**
```bash
# Using curl
curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/api/v1/users/
```

**Testing API (Windows PowerShell):**
```powershell
# Using Invoke-WebRequest
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/" -Headers @{"X-API-Key"="your-secret-api-key"}

# Or just use the interactive docs
# Navigate to http://localhost:8000/docs
```

### File Creation Order

1. **Model** (`app/db/models.py`) - Database schema
2. **Schemas** (`app/features/X/schemas.py`) - Pydantic models
3. **Service** (`app/features/X/service.py`) - Business logic
4. **Router** (`app/features/X/router.py`) - HTTP endpoints
5. **Register** (`app/api/v1/router.py`) - Include router
6. **Service Tests** (`tests/features/X/test_service.py`)
7. **Router Tests** (`tests/features/X/test_router.py`)

### Debugging Checklist

- [ ] Did I run the tests?
- [ ] Did I check the error message?
- [ ] Did I check what changed (git diff)?
- [ ] Are my dependencies up to date (uv sync)?
- [ ] Is my database clean (delete .db file)?
- [ ] Am I using the test database in tests?
- [ ] Did I add authentication where needed?
- [ ] Did I register my router?
- [ ] Did I add `__init__.py` files?

---

**Remember:** Every expert was once a beginner who refused to give up. These mistakes are how you learn. The key is to learn from them and not repeat them. 🚀
