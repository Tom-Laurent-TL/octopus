# Docker Deployment Guide

This guide covers deploying the Octopus API using Docker and Docker Compose.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Using Docker Directly

```bash
# Build the image
docker build -t octopus .

# Run the container (creates new volume each time)
docker run -p 8000:80 octopus

# Run with persistent database volume
docker run -p 8000:80 -v $(pwd)/data:/app/data octopus

# Run in detached mode
docker run -d -p 8000:80 -v $(pwd)/data:/app/data --name octopus-api octopus
```

## First Time Setup

### 1. Build the Image

```bash
docker-compose build
# or
docker build -t octopus .
```

### 2. Start the Container

```bash
docker-compose up -d
# or
docker run -d -p 8000:80 -v $(pwd)/data:/app/data --name octopus-api octopus
```

### 3. Bootstrap (Create Master API Key)

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/bootstrap" -Method Post
```

**Linux/Mac:**
```bash
curl -X POST http://localhost:8000/bootstrap
```

**Response:**
```json
{
  "message": "Bootstrap successful",
  "api_key": "octopus_abc123...",
  "scopes": "read,write,admin"
}
```

### 4. Save the API Key

Create a `.env` file in the project root:

```env
MASTER_API_KEY=octopus_abc123...your-key-here
DATABASE_URL=sqlite:////app/data/chat_conversations.db
```

### 5. Restart to Use the Master Key

```bash
docker-compose restart
# or
docker restart octopus-api
```

## Database Management

### Database Location

The database is stored in the `./data` directory on your host machine:
- **Host path**: `./data/chat_conversations.db`
- **Container path**: `/app/data/chat_conversations.db`

### Database Migrations

This project uses **Alembic** for database schema migrations. Migrations are automatically applied when the container starts.

**How it works:**
- The Docker entrypoint script runs `alembic upgrade head` on startup
- This applies any pending database migrations
- Safe to run multiple times - only applies new migrations

**To manually run migrations:**
```bash
# Inside the container
docker-compose exec app alembic upgrade head

# Check current migration version
docker-compose exec app alembic current

# View migration history
docker-compose exec app alembic history
```

**For more details**, see the comprehensive [Database Migrations Guide](DATABASE_MIGRATIONS.md).

### Reset Database

To start with a fresh database:

```bash
# Stop the container
docker-compose down

# Delete the database
rm -rf ./data/chat_conversations.db
# or on Windows PowerShell:
Remove-Item -Path .\data\chat_conversations.db -Force

# Start the container (creates new database and applies migrations)
docker-compose up -d

# Bootstrap again (create new master key)
curl -X POST http://localhost:8000/bootstrap
```

### Backup Database

```bash
# Copy from container to host
docker cp octopus-api:/app/data/chat_conversations.db ./backup_$(date +%Y%m%d).db

# Or if using volume (recommended)
cp ./data/chat_conversations.db ./backup_$(date +%Y%m%d).db
```

### Restore Database

```bash
# Stop the container
docker-compose down

# Replace the database
cp ./backup_YYYYMMDD.db ./data/chat_conversations.db

# Start the container
docker-compose up -d
```

## Environment Variables

The application uses environment variables for configuration. Docker Compose **automatically overrides** the `.env` file settings for Docker-specific paths.

### Configuration Priority

1. **docker-compose.yml** environment section (highest priority - used in Docker)
2. **.env file** (used for local development)
3. **Default values** in code (fallback)

### Local Development (.env file)

```env
MASTER_API_KEY=your-secret-api-key-here
DATABASE_URL=sqlite:///./chat_conversations.db
```

This configuration is used when running with `uv run fastapi dev` or `uv run fastapi run`.

### Docker Configuration

Docker Compose **automatically sets** the correct database path. You don't need to change your `.env` file!

The `docker-compose.yml` file overrides `DATABASE_URL`:

```yaml
environment:
  - DATABASE_URL=sqlite:////app/data/chat_conversations.db  # Docker path
  - MASTER_API_KEY=${MASTER_API_KEY:-}                     # From .env file
```

**Key Points:**
- ✅ Keep `.env` with local development paths
- ✅ Docker Compose automatically uses Docker paths
- ✅ No need to manually change DATABASE_URL for Docker
- ✅ Database is stored in `./data/` directory on your host

### Setting the Master API Key

After bootstrap, update your `.env` file:

```env
MASTER_API_KEY=octopus_abc123...your-actual-key-here
DATABASE_URL=sqlite:///./chat_conversations.db
```

Then restart Docker to use the new key:

```bash
docker-compose restart
```

## Accessing the API

Once the container is running:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## Common Commands

### Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f octopus

# Rebuild and restart
docker-compose up -d --build

# Execute command in container
docker-compose exec octopus /bin/bash

# Scale services (not typically needed for this app)
docker-compose up -d --scale octopus=2
```

### Docker

```bash
# List running containers
docker ps

# View logs
docker logs -f octopus-api

# Execute command in container
docker exec -it octopus-api /bin/bash

# Stop container
docker stop octopus-api

# Start container
docker start octopus-api

# Remove container
docker rm octopus-api

# Remove image
docker rmi octopus
```

## Production Deployment

### Using Docker Compose

1. **Update docker-compose.yml** for production:

```yaml
version: '3.8'

services:
  octopus:
    build: .
    container_name: octopus-api
    ports:
      - "8000:80"
    volumes:
      - ./data:/app/data
    environment:
      - MASTER_API_KEY=${MASTER_API_KEY}
      - DATABASE_URL=sqlite:////app/data/chat_conversations.db
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

2. **Set up environment variables**:

```bash
echo "MASTER_API_KEY=your_actual_master_key" > .env
```

3. **Deploy**:

```bash
docker-compose up -d
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml octopus

# List services
docker stack services octopus

# Remove stack
docker stack rm octopus
```

### Using Kubernetes

Create a deployment file `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: octopus-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: octopus-api
  template:
    metadata:
      labels:
        app: octopus-api
    spec:
      containers:
      - name: octopus-api
        image: octopus:latest
        ports:
        - containerPort: 80
        env:
        - name: MASTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: octopus-secrets
              key: master-api-key
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: octopus-data
---
apiVersion: v1
kind: Service
metadata:
  name: octopus-api
spec:
  selector:
    app: octopus-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f k8s-deployment.yaml
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Check if port is already in use
netstat -an | grep 8000

# Try different port
docker run -p 8001:80 octopus
```

### Database Errors

**Error: `no such column: api_keys.last_used_ip`**

This means your database has the old schema. The automatic migrations should fix this, but if not:

```bash
# Option 1: Let migrations run (should happen automatically)
docker-compose restart

# Option 2: Reset database (loses all data)
docker-compose down
rm ./data/chat_conversations.db
docker-compose up -d
curl -X POST http://localhost:8000/bootstrap
```

### Permission Issues

```bash
# Fix permissions on data directory
chmod 755 ./data
chmod 644 ./data/chat_conversations.db
```

### Container Crashes on Startup

```bash
# View detailed logs
docker-compose logs -f

# Check if database directory exists
mkdir -p ./data

# Verify Dockerfile builds correctly
docker build -t octopus .
```

### "alembic: command not found" Error

**Error**: Container exits with `alembic: command not found` or `fastapi: command not found`.

**Cause**: When using `uv` package manager, executables are installed in the virtual environment at `/app/.venv/bin/`, which may not be in the container's PATH.

**Solution**: The `docker-entrypoint.sh` script should use full paths to executables:

```bash
#!/bin/bash
set -e

# Use full path to alembic
/app/.venv/bin/alembic upgrade head

# Use full path to fastapi
exec /app/.venv/bin/fastapi run app/main.py --host 0.0.0.0 --port 80
```

This issue has been fixed in the current codebase. If you encounter it:
1. Update your `docker-entrypoint.sh` with the full paths above
2. Rebuild: `docker-compose down && docker-compose up --build`

## Health Checks

The container includes a health check that pings the `/health` endpoint:

```bash
# Check container health
docker ps

# The STATUS column shows health:
# - starting (initial startup)
# - healthy (working correctly)
# - unhealthy (failing health checks)
```

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Migrations run automatically on startup
```

## Best Practices

1. **Always use volumes** for database persistence
2. **Back up the database** before updates
3. **Use .env files** for sensitive configuration
4. **Monitor logs** regularly
5. **Set up health checks** in production
6. **Use docker-compose** for easier management
7. **Keep images updated** for security patches

## Security Considerations

1. **Never commit `.env` files** with real API keys
2. **Use secrets management** in production (Docker secrets, Kubernetes secrets)
3. **Restrict port exposure** to necessary ports only
4. **Run as non-root user** (can add to Dockerfile)
5. **Keep Docker images updated** for security patches
6. **Use HTTPS** in production (add reverse proxy like nginx or Traefik)

## Performance Tuning

For production workloads:

1. **Use PostgreSQL** instead of SQLite:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/octopus
   ```

2. **Increase workers** (update Dockerfile):
   ```dockerfile
   CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--workers", "4"]
   ```

3. **Add Redis** for rate limiting (update docker-compose.yml):
   ```yaml
   services:
     redis:
       image: redis:alpine
       ports:
         - "6379:6379"
   ```

---

**For more information, see**:
- [Main README](../README.md)
- [API Key Security](../docs/API_KEY_SECURITY.md)
- [Project Structure](../docs/PROJECT_STRUCTURE.md)
