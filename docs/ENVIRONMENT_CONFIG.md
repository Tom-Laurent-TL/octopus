# Environment Configuration Guide

This guide explains how to configure environment variables for local development and Docker deployments.

## Quick Reference

| Scenario | Database Path | Config File |
|----------|---------------|-------------|
| **Local Development** | `sqlite:///./data/chat_conversations.db` | `.env` |
| **Docker/Docker Compose** | `sqlite:////app/data/chat_conversations.db` | `docker-compose.yml` (auto-override) |

## Setup

### 1. Create Your .env File

```bash
# Copy the example file
cp .env.example .env

# Or create manually
cat > .env << 'EOF'
MASTER_API_KEY=your-secret-api-key-here
DATABASE_URL=sqlite:///./data/chat_conversations.db
EOF
```

### 2. Run Bootstrap

**Local Development:**
```bash
uv run fastapi dev app/main.py
curl -X POST http://localhost:8000/bootstrap
```

**Docker:**
```bash
docker-compose up -d
curl -X POST http://localhost:8000/bootstrap
```

### 3. Update .env with Master Key

After bootstrap returns your key, update `.env`:

```env
MASTER_API_KEY=octopus_abc123...your-actual-key-here
DATABASE_URL=sqlite:///./chat_conversations.db
```

### 4. Restart

**Local Development:**
```bash
# Stop with Ctrl+C, then:
uv run fastapi dev app/main.py
```

**Docker:**
```bash
docker-compose restart
```

## Configuration Details

### Environment Variables

#### MASTER_API_KEY
- **Purpose**: Authenticates admin-level API requests
- **Format**: `octopus_` prefix + random characters
- **When to set**: After running bootstrap endpoint
- **Security**: Never commit this to git (`.env` is in `.gitignore`)

#### DATABASE_URL
- **Purpose**: Specifies database location
- **Format**: SQLAlchemy database URL
- **Local**: `sqlite:///./data/chat_conversations.db` (relative path, 3 slashes)
- **Docker**: `sqlite:////app/data/chat_conversations.db` (absolute path, 4 slashes)
- **Note**: Database is stored in `data/` folder for clean organization

### SQLite URL Format

```
sqlite:///./data/file.db    = Relative path (3 slashes, ./data/ folder)
sqlite:////absolute/path    = Absolute path (4 slashes total)
```

Examples:
```
sqlite:///./data.db                      = Relative: ./data.db
sqlite:////tmp/data.db                   = Absolute: /tmp/data.db
sqlite:///C:/Users/name/data.db          = Windows absolute path
```

## How Docker Overrides Work

### The Problem

Your `.env` file has local paths, but Docker needs different paths.

### The Solution

Docker Compose's `environment` section **overrides** .env variables:

```yaml
# docker-compose.yml
services:
  octopus:
    environment:
      # This overrides DATABASE_URL from .env
      - DATABASE_URL=sqlite:////app/data/chat_conversations.db
      # This reads from .env file
      - MASTER_API_KEY=${MASTER_API_KEY:-}
```

**Result:**
- ✅ Local development uses `.env` paths
- ✅ Docker uses `docker-compose.yml` paths
- ✅ Same `.env` file works for both!

## Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore already includes:
.env
```

But `.env.example` is committed (without secrets).

### 2. Use .env.example as Template

When setting up a new environment:

```bash
cp .env.example .env
# Then edit .env with actual values
```

### 3. Document Environment Variables

Keep `.env.example` updated with:
- All required variables
- Example values (not real secrets)
- Comments explaining each variable

### 4. Validate Configuration

Check if your configuration is correct:

```bash
# Local
uv run python -c "from app.core.config import settings; print(settings.database_url)"

# Docker
docker-compose exec octopus python -c "from app.core.config import settings; print(settings.database_url)"
```

## Troubleshooting

### Issue: "Wrong database path in Docker"

**Symptom**: Docker creates database in wrong location

**Solution**: Docker Compose automatically overrides the path. Just use:
```bash
docker-compose up -d
```

The database will be in `./data/chat_conversations.db` on your host.

### Issue: "Database not persisting in Docker"

**Symptom**: Data lost when container restarts

**Check volume mount:**
```bash
docker-compose down
docker-compose up -d
ls ./data/  # Should see chat_conversations.db
```

If missing, check `docker-compose.yml` has:
```yaml
volumes:
  - ./data:/app/data
```

### Issue: "Can't find .env file"

**Symptom**: Application can't load environment variables

**Solution**: Create from template:
```bash
cp .env.example .env
```

### Issue: "Different database in local vs Docker"

**Both now use the same location!** `data/chat_conversations.db`
- **Local**: `./data/chat_conversations.db` (via `.env`)
- **Docker**: `./data/chat_conversations.db` (volume mounted)

This provides consistency between local and Docker environments.

## Switching Between Environments

### From Local to Docker

```bash
# Stop local server (Ctrl+C)

# Start Docker
docker-compose up -d
```

**Note**: Since both use `data/chat_conversations.db`, your data is already shared!
No need to bootstrap again - your existing data will work in Docker.

### From Docker to Local

```bash
# Stop Docker
docker-compose down

# Start local
uv run fastapi dev app/main.py

# Bootstrap if needed
curl -X POST http://localhost:8000/bootstrap
```

## Production Configuration

For production, use **environment-specific** configurations:

### Docker Swarm / Kubernetes

Use secrets management:

```yaml
# docker-compose.prod.yml
services:
  octopus:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/octopus
    secrets:
      - master_api_key

secrets:
  master_api_key:
    external: true
```

### Cloud Platforms

Use platform-specific secrets:

**AWS ECS:**
```json
{
  "secrets": [
    {
      "name": "MASTER_API_KEY",
      "valueFrom": "arn:aws:secretsmanager:region:account:secret:name"
    }
  ]
}
```

**Azure Container Instances:**
```bash
az container create \
  --secure-environment-variables MASTER_API_KEY=value
```

## Summary

✅ **Keep .env with local paths** - Docker overrides automatically  
✅ **Use docker-compose.yml for Docker config** - No need to change .env  
✅ **Never commit .env** - Use .env.example instead  
✅ **Separate databases per environment** - Local and Docker are independent  
✅ **Copy database when switching** - If you need the same data  

---

**For more information, see:**
- [Main README](../README.md)
- [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Configuration Settings](../app/core/config.py)
