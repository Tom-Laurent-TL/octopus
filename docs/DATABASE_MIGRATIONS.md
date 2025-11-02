# Database Migrations with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations, providing version-controlled, repeatable database changes.

## Table of Contents
- [Quick Start](#quick-start)
- [Common Commands](#common-commands)
- [Creating Migrations](#creating-migrations)
- [Applying Migrations](#applying-migrations)
- [Migration Workflow](#migration-workflow)
- [Docker Considerations](#docker-considerations)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Quick Start

### First Time Setup (Existing Database)

If you already have a database, mark it as being at the current baseline:

```bash
# Mark existing database as at baseline
uv run alembic stamp head

# Verify
uv run alembic current
```

### Creating a New Database

```bash
# Apply all migrations
uv run alembic upgrade head
```

## Common Commands

```bash
# Check current migration version
uv run alembic current

# Show migration history
uv run alembic history

# Apply all pending migrations
uv run alembic upgrade head

# Apply one migration forward
uv run alembic upgrade +1

# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific version
uv run alembic downgrade <revision_id>

# Create a new migration
uv run alembic revision -m "description"

# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "description"
```

## Creating Migrations

### Auto-generate from Model Changes

The recommended way is to let Alembic detect changes:

1. **Modify your models** in `app/db/models.py`
2. **Generate migration**:
   ```bash
   uv run alembic revision --autogenerate -m "Add user profile fields"
   ```
3. **Review the generated file** in `alembic/versions/`
4. **Edit if needed** (Alembic isn't perfect, especially with SQLite)
5. **Apply the migration**:
   ```bash
   uv run alembic upgrade head
   ```

### Manual Migration

For complex changes or SQLite limitations:

```bash
# Create empty migration file
uv run alembic revision -m "complex schema change"
```

Edit the generated file:

```python
def upgrade() -> None:
    """Upgrade schema."""
    # Add your SQL operations here
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the operations
    op.drop_index('ix_users_email', 'users')
    op.drop_column('users', 'bio')
```

## Applying Migrations

### Development

```bash
# Apply all pending migrations
uv run alembic upgrade head
```

### Production

```bash
# 1. Backup database
cp chat_conversations.db chat_conversations.db.backup

# 2. Apply migrations
uv run alembic upgrade head

# 3. Verify application works
# If issues, rollback:
uv run alembic downgrade -1
```

### Docker

Migrations are automatically applied on container startup. See [Docker Considerations](#docker-considerations).

## Migration Workflow

### Adding a New Feature with Database Changes

1. **Create model** in `app/db/models.py`:
   ```python
   class Profile(Base):
       __tablename__ = "profiles"
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, ForeignKey("users.id"))
       bio = Column(Text)
   ```

2. **Generate migration**:
   ```bash
   uv run alembic revision --autogenerate -m "Add profiles table"
   ```

3. **Review generated migration** in `alembic/versions/`:
   - Check it does what you expect
   - SQLite has limited ALTER TABLE support
   - May need manual adjustments

4. **Apply migration**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Test** thoroughly:
   ```bash
   uv run pytest
   ```

6. **Commit** both model changes and migration file:
   ```bash
   git add app/db/models.py alembic/versions/*.py
   git commit -m "Add profiles feature"
   ```

### Team Workflow

When pulling changes with new migrations:

```bash
# Pull latest code
git pull

# Check if there are pending migrations
uv run alembic current
uv run alembic history

# Apply new migrations
uv run alembic upgrade head

# Run tests to verify
uv run pytest
```

### Handling Migration Conflicts

If two developers create migrations simultaneously:

1. **Identify the conflict** - you'll have two migrations with the same down_revision
2. **Choose migration order**
3. **Update down_revision** in one migration to reference the other
4. **Test the migration chain**:
   ```bash
   # Rollback to before the conflict
   uv run alembic downgrade <earlier_revision>
   
   # Apply both in order
   uv run alembic upgrade head
   ```

## Docker Considerations

### Dockerfile

Migrations run automatically on container startup via the entrypoint script.

Update your `Dockerfile` or create an entrypoint script:

```dockerfile
# Copy alembic files
COPY alembic.ini ./
COPY alembic ./alembic

# Entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
```

### docker-entrypoint.sh

```bash
#!/bin/bash
set -e

# Run migrations (use full path to alembic in uv's virtual environment)
echo "Running database migrations..."
/app/.venv/bin/alembic upgrade head

# Start the application (use full path to fastapi)
exec /app/.venv/bin/fastapi run app/main.py --host 0.0.0.0 --port 80
```

**Important**: When using `uv` package manager, executables are installed in `/app/.venv/bin/`. Use full paths in shell scripts since the virtual environment may not be activated.

### Docker Compose

```yaml
services:
  app:
    build: .
    volumes:
      - ./data:/app/data  # Persist database
    environment:
      - DATABASE_URL=sqlite:////app/data/chat_conversations.db
```

## Troubleshooting

### "Table already exists" Error

If you get errors about existing tables:

```bash
# Mark database as at current version without running migrations
uv run alembic stamp head
```

### SQLite Limitations

SQLite doesn't support many ALTER TABLE operations:
- Can't drop columns
- Can't alter column types
- Can't rename columns (without recreating table)

**Solutions**:
1. **For development**: Delete database and recreate
2. **For production**: Write manual migration with table recreation
3. **Avoid**: Use PostgreSQL/MySQL for production if you need complex migrations

Example of table recreation migration:

```python
def upgrade() -> None:
    # Create new table with desired schema
    op.create_table(
        'users_new',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False),
        # ... new schema
    )
    
    # Copy data
    op.execute('''
        INSERT INTO users_new (id, username)
        SELECT id, username FROM users
    ''')
    
    # Drop old table
    op.drop_table('users')
    
    # Rename new table
    op.rename_table('users_new', 'users')
```

### Migration Failed Mid-way

Alembic uses transactions, but SQLite's transaction support varies:

```bash
# Check current state
uv run alembic current

# If migration partially applied, manual fix needed:
# 1. Check database schema manually
# 2. Fix the migration file
# 3. Mark as at previous version:
uv run alembic stamp <previous_revision>

# 4. Try again:
uv run alembic upgrade head
```

### "Can't locate revision" Error

If Alembic can't find a revision:

```bash
# Check history
uv run alembic history

# Database might be ahead of code, or migration files missing
# Reset to known good state:
uv run alembic stamp <known_good_revision>
```

## Best Practices

### ✅ DO

1. **Always review auto-generated migrations** - they're not perfect
2. **Test migrations on a copy** of production data
3. **Backup before production migrations**
4. **Keep migrations small** - one logical change per migration
5. **Write reversible migrations** - implement both upgrade() and downgrade()
6. **Commit migration files** to version control
7. **Document complex migrations** with comments
8. **Test both upgrade and downgrade**:
   ```bash
   uv run alembic upgrade head
   uv run alembic downgrade -1
   uv run alembic upgrade head
   ```

### ❌ DON'T

1. **Don't edit migrations after they're applied** in production
2. **Don't delete migrations** from version history
3. **Don't assume SQLite supports all operations** - test carefully
4. **Don't skip migration testing** - always test before production
5. **Don't mix manual schema changes** with Alembic - use migrations only
6. **Don't commit with failing migrations** - fix them first

### Migration Naming

Use descriptive names:

```bash
# ✅ Good
uv run alembic revision -m "add user profile fields"
uv run alembic revision -m "create audit log table"
uv run alembic revision -m "add index on user email"

# ❌ Bad
uv run alembic revision -m "update"
uv run alembic revision -m "fix"
uv run alembic revision -m "changes"
```

### Schema Changes Requiring Migrations

**Always use Alembic for**:
- Adding/removing tables
- Adding/removing columns
- Changing column types
- Adding/removing indexes
- Adding/removing constraints
- Data migrations

**Example - Data Migration**:

```python
def upgrade() -> None:
    # Add column
    op.add_column('users', sa.Column('status', sa.String(20), nullable=True))
    
    # Populate with default data
    op.execute("UPDATE users SET status = 'active' WHERE is_active = 1")
    op.execute("UPDATE users SET status = 'inactive' WHERE is_active = 0")
    
    # Make not nullable
    op.alter_column('users', 'status', nullable=False)
```

## PostgreSQL vs SQLite

This project uses SQLite for development, but you may want PostgreSQL for production:

### Switching to PostgreSQL

1. **Update DATABASE_URL** in `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/octopus
   ```

2. **Install asyncpg**:
   ```bash
   uv add asyncpg
   ```

3. **Migrations work the same way** - Alembic handles the differences

4. **Benefits**:
   - Full ALTER TABLE support
   - Better concurrent write handling
   - No SQLite limitations
   - Production-ready

## Additional Resources

- [Alembic Official Docs](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI + Alembic](https://fastapi.tiangolo.com/tutorial/sql-databases/)

## Migration History

Current migrations in this project:

| Revision | Description | Date |
|----------|-------------|------|
| 99b3ff7741d5 | Initial schema baseline | 2025-11-02 |

---

**Next Steps**: Read [Feature Implementation Guide](FEATURE_IMPLEMENTATION_GUIDE.md) to learn how to add new features with database changes.
