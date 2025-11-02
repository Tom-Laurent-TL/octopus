# API Key Management System

## Overview

The Octopus API now uses a **production-ready database-backed API key system** with fine-grained access control through scopes.

## Key Features

✅ **Multiple API Keys** - Create and manage multiple API keys with different permissions  
✅ **Scope-Based Access Control** - Read, write, and admin scopes for granular permissions  
✅ **Usage Tracking** - Automatic tracking of last used timestamp and IP address  
✅ **Key Expiration** - Optional expiration dates for temporary access with automatic cleanup  
✅ **Secure Key Generation** - Cryptographically secure random keys with `octopus_` prefix  
✅ **Soft Delete** - Deactivate keys without losing audit trail  
✅ **Safety Features** - Cannot delete or deactivate the key you're currently using  
✅ **Rate Limiting** - Protection against brute force attacks (10 req/min for auth)  
✅ **Audit Logging** - Complete audit trail of all key operations  
✅ **IP Whitelisting** - Restrict keys to specific IP addresses  
✅ **Key Rotation** - Built-in support for automated key rotation  
✅ **Monitoring** - Structured logging for failed authentication attempts  

**See [API Key Security Features](API_KEY_SECURITY.md) for detailed security documentation.**

## Quick Start

### 1. Start the Server

```bash
uv run fastapi dev app/main.py
```

### 2. Bootstrap (First Time Only)

Call the bootstrap endpoint (in `app/core/bootstrap.py`) to create your master API key:

**Windows PowerShell:**
```powershell
# Use the provided script
.\scripts\bootstrap.ps1

# Or manually:
Invoke-RestMethod -Uri "http://localhost:8000/bootstrap" -Method Post
```

**Linux/Mac/WSL:**
```bash
curl -X POST http://localhost:8000/bootstrap
```

This creates:
- A master API key with full admin access
- Returns the key (save it securely!)

**Important:** This endpoint can only be called once - when no API keys exist.

### 3. Save Your Master Key

Add the returned key to your `.env` file:

```env
MASTER_API_KEY=octopus_xyz...your-key-here
```

### 4. Use Your API Key

```bash
# Linux/Mac/WSL
curl -H "Octopus-API-Key: your-key-here" http://localhost:8000/api/v1/users/

# Windows PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/" -Headers @{"Octopus-API-Key"="your-key-here"}
```

### 5. Manage API Keys

Use the interactive PowerShell script:

```powershell
# Set your master key
$env:API_KEY = "your-master-key-here"

# Run the management script
.\scripts\manage-api-keys.ps1
```

Or create additional keys via API:

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Octopus-API-Key: your-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Read-Only Monitoring",
    "description": "For monitoring dashboard",
    "scopes": "read"
  }'
```

## Available Scopes

| Scope | Description |
|-------|-------------|
| `read` | Read-only access to resources |
| `write` | Create and update resources |
| `admin` | Full access including API key management |

**Note:** Admin scope grants access to everything, including other scopes.

## API Endpoints

All endpoints require an API key with `admin` scope.

### Create API Key
```http
POST /api/v1/api-keys/
```
**Returns:** The complete key (only shown once!)

### List API Keys
```http
GET /api/v1/api-keys/
```
**Query Parameters:**
- `skip` - Pagination offset (default: 0)
- `limit` - Results per page (default: 100)
- `include_inactive` - Include deactivated keys (default: false)

### Get API Key
```http
GET /api/v1/api-keys/{id}
```

### Update API Key
```http
PATCH /api/v1/api-keys/{id}
```
Update name, description, scopes, active status, or expiration.

### Deactivate API Key
```http
POST /api/v1/api-keys/{id}/deactivate
```
Soft delete - key remains in database for audit purposes.

### Delete API Key
```http
DELETE /api/v1/api-keys/{id}
```
Permanent deletion. ⚠️ This cannot be undone!

### Rotate API Key
```http
POST /api/v1/api-keys/{id}/rotate
```
Creates new key with same properties, deactivates old key. Returns new key value.

### Get Audit Logs
```http
GET /api/v1/api-keys/audit-logs/
```
**Query Parameters:**
- `api_key_id` - Filter by specific key
- `action` - Filter by action (create, update, delete, etc.)
- `skip` - Pagination offset
- `limit` - Results per page

### Get Expiring Keys
```http
GET /api/v1/api-keys/expiring/
```
**Query Parameters:**
- `days` - Days until expiration (default: 7)

### Cleanup Expired Keys
```http
POST /api/v1/api-keys/cleanup-expired/
```
Deactivates all expired keys. Returns count of deactivated keys.

## Database Schema

```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,           -- The actual API key
    name VARCHAR(255) NOT NULL,                 -- Friendly name
    description TEXT,                           -- Optional description
    scopes VARCHAR(500) NOT NULL DEFAULT 'read', -- Comma-separated scopes
    is_active BOOLEAN NOT NULL DEFAULT TRUE,    -- Active/inactive status
    created_at DATETIME NOT NULL,               -- Creation timestamp
    last_used_at DATETIME,                      -- Last usage timestamp
    last_used_ip VARCHAR(45),                   -- Last IP address used from
    expires_at DATETIME,                        -- Optional expiration
    allowed_ips TEXT,                           -- Comma-separated allowed IPs
    created_by_user_id INTEGER,                 -- Optional user reference
    FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);

CREATE TABLE api_key_audit_logs (
    id INTEGER PRIMARY KEY,
    api_key_id INTEGER,                         -- Key that was affected
    action VARCHAR(50) NOT NULL,                -- Action performed
    performed_by_key_id INTEGER,                -- Key that performed action
    performed_by_ip VARCHAR(45),                -- IP address of request
    details TEXT,                               -- JSON with additional details
    timestamp DATETIME NOT NULL,                -- When action occurred
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id),
    FOREIGN KEY (performed_by_key_id) REFERENCES api_keys(id)
);
```

## Security Best Practices

### ✅ DO

- Store API keys securely (environment variables, secrets manager)
- Use specific scopes (principle of least privilege)
- Set expiration dates for temporary access
- Regularly rotate API keys (every 90 days recommended)
- Deactivate unused keys
- Monitor last_used_at timestamps and audit logs
- Use IP whitelisting for production systems
- Review audit logs regularly
- Set up alerts for failed authentication attempts
- Run cleanup script daily to deactivate expired keys

### ❌ DON'T

- Commit API keys to version control
- Share admin keys unnecessarily
- Use the same key across multiple services
- Forget to deactivate keys when no longer needed
- Ignore failed authentication attempts
- Skip key rotation

## Advanced Features

For detailed documentation on:
- **Rate Limiting**
- **Audit Logging**
- **Monitoring & Alerting**
- **IP Whitelisting**
- **Key Expiration Management**
- **Automated Key Rotation**

See **[API Key Security Features](API_KEY_SECURITY.md)**

## Migration from Single API Key

If you have existing code using the old single-key system:

1. Run bootstrap endpoint to create master key
2. Update your `.env` file with the new master key
3. All existing code will continue to work!
4. Gradually migrate to using specific-scope keys for different services

## Testing

The system includes comprehensive tests:
- 24 API key-specific tests
- Full test coverage for all CRUD operations
- Security tests (expired keys, inactive keys, scope validation)
- Integration tests with existing features

```bash
# Run API key tests
uv run pytest tests/features/api_keys/ -v

# Run all tests
uv run pytest -v
```

## Architecture

Following the project's feature-based architecture:

```
app/
├── core/
│   ├── config.py      # Application settings
│   ├── security.py    # Authentication verification
│   └── bootstrap.py   # System initialization endpoint
│
├── features/api_keys/
│   ├── __init__.py
│   ├── router.py      # HTTP endpoints
│   ├── service.py     # Business logic (key generation, validation)
│   └── schemas.py     # Pydantic models
│
└── db/models.py       # APIKey model
```

## Examples

### Create a Read-Only Key
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/api-keys/",
    headers={"Octopus-API-Key": "your-master-key"},
    json={
        "name": "Analytics Dashboard",
        "description": "Read-only access for reporting",
        "scopes": "read"
    }
)
key_data = response.json()
print(f"New key: {key_data['key']}")  # Save this!
```

### Create a Temporary Key
```python
from datetime import datetime, timedelta, UTC

expires_at = (datetime.now(UTC) + timedelta(days=7)).isoformat()

response = requests.post(
    "http://localhost:8000/api/v1/api-keys/",
    headers={"Octopus-API-Key": "your-master-key"},
    json={
        "name": "Temporary Access",
        "description": "7-day access for contractor",
        "scopes": "read,write",
        "expires_at": expires_at
    }
)
```

### List All Active Keys
```python
response = requests.get(
    "http://localhost:8000/api/v1/api-keys/",
    headers={"Octopus-API-Key": "your-master-key"}
)
keys = response.json()
for key in keys:
    print(f"{key['name']}: {key['scopes']} (last used: {key['last_used_at']})")
```

## Troubleshooting

### "Invalid or inactive API Key"
- Check that the key is active: `GET /api/v1/api-keys/`
- Verify you're using the correct header: `Octopus-API-Key`
- Ensure the key hasn't been deactivated

### "API Key has expired"
- The key has passed its `expires_at` date
- Create a new key or update the expiration date

### "Admin scope required"
- Only keys with `admin` scope can manage other keys
- Use your master key for API key management

## Future Enhancements

Potential additions:
- Rate limiting per key
- IP whitelisting
- Key rotation automation
- Usage analytics dashboard
- Webhook notifications for key events
