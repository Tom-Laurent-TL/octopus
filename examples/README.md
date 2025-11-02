# API Examples

This folder contains curl command examples and a Python demo script for interacting with the Octopus API.

All curl examples work cross-platform (Windows, Linux, macOS).

---

## 🎬 Quick Demo

Want to see everything in action? Run the end-to-end Python demo script:

```bash
# All platforms (Windows, Linux, macOS)
python examples/demo.py

# Or with uv
uv run python examples/demo.py
```

The demo script will:
- ✅ Create master API key
- ✅ Create additional API keys with different scopes
- ✅ Create multiple users (Alice, Bob, Charlie, Diana)
- ✅ Create conversations with participants
- ✅ Send messages between users
- ✅ Manage participants (add/remove)
- ✅ Update user information
- ✅ Display all created resources with IDs

**Requirements:** The script uses `httpx` library (already in project dependencies).

---

## 📋 Prerequisites

- API server running at `http://localhost:8000`
- An API key (get one from bootstrap)

---

## 🚀 Quick Start

### 1. Bootstrap (First Time Setup)

Create your master API key:

```bash
curl -X POST http://localhost:8000/bootstrap
```

**Response:**
```json
{
  "message": "Bootstrap successful",
  "api_key": "octopus_abc123...",
  "name": "Master Key",
  "scopes": "read,write,admin"
}
```

**Important**: Save the API key! Add it to your `.env` file:
```env
MASTER_API_KEY=octopus_abc123...your-key-here
```

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

---

## 🔐 API Key Management

Set your API key in an environment variable:

**Linux/macOS/WSL:**
```bash
export API_KEY="your-api-key-here"
```

**Windows PowerShell:**
```powershell
$env:API_KEY = "your-api-key-here"
```

**Windows CMD:**
```cmd
set API_KEY=your-api-key-here
```

### List All API Keys

**Linux/macOS/WSL:**
```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/api-keys/
```

**Windows PowerShell:**
```powershell
curl.exe -H "Octopus-API-Key: $env:API_KEY" http://localhost:8000/api/v1/api-keys/
```

### Create New API Key

**Linux/macOS/WSL:**
```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Development Key",
    "description": "Key for local development",
    "scopes": "read,write"
  }' \
  http://localhost:8000/api/v1/api-keys/
```

**Windows PowerShell:**
```powershell
curl.exe -X POST `
  -H "Octopus-API-Key: $env:API_KEY" `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Development Key\",\"description\":\"Key for local development\",\"scopes\":\"read,write\"}' `
  http://localhost:8000/api/v1/api-keys/
```

### Create Key with Expiration

```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Temporary Key",
    "scopes": "read",
    "expires_at": "2025-12-31T23:59:59Z"
  }' \
  http://localhost:8000/api/v1/api-keys/
```

### Get API Key Details

```bash
# Replace {key_id} with the actual key ID
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/api-keys/{key_id}
```

### Update API Key

```bash
curl -X PATCH \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Key Name",
    "description": "Updated description"
  }' \
  http://localhost:8000/api/v1/api-keys/{key_id}
```

### Deactivate API Key

```bash
curl -X PATCH \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}' \
  http://localhost:8000/api/v1/api-keys/{key_id}
```

### Delete API Key

```bash
curl -X DELETE \
  -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/api-keys/{key_id}
```

### Rotate API Key

```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/api-keys/{key_id}/rotate
```

---

## 👥 User Management

### Create User

```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "secure-password-123",
    "full_name": "Alice Smith"
  }' \
  http://localhost:8000/api/v1/users/
```

### Get User by ID

```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/users/{user_id}
```

### Get User by Username

```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/users/username/alice
```

### List All Users

```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/users/
```

### Update User

```bash
curl -X PATCH \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Alice Johnson",
    "email": "alice.j@example.com"
  }' \
  http://localhost:8000/api/v1/users/{user_id}
```

### Delete User

```bash
curl -X DELETE \
  -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/users/{user_id}
```

---

## 💬 Conversations

### Create Conversation

```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Discussion",
    "participant_ids": [1, 2, 3]
  }' \
  http://localhost:8000/api/v1/conversations/
```

### Get Conversation

```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/conversations/{conversation_id}
```

### List All Conversations

```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/conversations/
```

### List User's Conversations

```bash
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/conversations/user/{user_id}
```

### Add Message to Conversation

```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Hello everyone!",
    "user_id": 1
  }' \
  http://localhost:8000/api/v1/conversations/{conversation_id}/messages
```

### Add Participant to Conversation

```bash
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 4}' \
  http://localhost:8000/api/v1/conversations/{conversation_id}/participants
```

### Remove Participant from Conversation

```bash
curl -X DELETE \
  -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/conversations/{conversation_id}/participants/{user_id}
```

### Delete Conversation

```bash
curl -X DELETE \
  -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/conversations/{conversation_id}
```

---

## 🔄 Complete Workflow Example

Here's a complete example workflow:

```bash
# 1. Bootstrap (first time only)
curl -X POST http://localhost:8000/bootstrap

# 2. Save your API key
export API_KEY="octopus_abc123..."

# 3. Create users
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","username":"alice","password":"pass123","full_name":"Alice Smith"}' \
  http://localhost:8000/api/v1/users/

curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","username":"bob","password":"pass123","full_name":"Bob Jones"}' \
  http://localhost:8000/api/v1/users/

# 4. Create conversation (use user IDs from step 3)
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Alice and Bob Chat","participant_ids":[1,2]}' \
  http://localhost:8000/api/v1/conversations/

# 5. Add message (use conversation ID from step 4)
curl -X POST \
  -H "Octopus-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"role":"user","content":"Hi Bob!","user_id":1}' \
  http://localhost:8000/api/v1/conversations/1/messages

# 6. Get conversation with all messages
curl -H "Octopus-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/conversations/1
```

---

## 📖 Windows PowerShell Notes

PowerShell has `curl` as an alias for `Invoke-WebRequest`, which works differently.

**Solution**: Use `curl.exe` explicitly:
```powershell
**Windows PowerShell:**
```powershell
curl.exe -H "Octopus-API-Key: $env:API_KEY" http://localhost:8000/api/v1/users/
```

Or install curl for Windows: https://curl.se/windows/

---

## 📚 More Information

- [Main README](../README.md) - Project overview
- [API Key Security Guide](../docs/API_KEY_SECURITY.md) - Security best practices
- [Feature Implementation Guide](../docs/FEATURE_IMPLEMENTATION_GUIDE.md) - Building features
- [Database Migrations](../docs/DATABASE_MIGRATIONS.md) - Managing database schema
```

Or install curl for Windows: https://curl.se/windows/

---

## 🔍 Interactive API Documentation

For an interactive interface with forms and validation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📜 Legacy PowerShell Scripts

This folder also contains PowerShell scripts for Windows users who prefer PowerShell:

- `bootstrap.ps1` - Bootstrap the application (create master key)
- `manage-api-keys.ps1` - Interactive API key management menu
- `test-api.ps1` - Test API endpoints
- `test-conversations.ps1` - Test conversation features

**Usage:**
```powershell
.\examples\bootstrap.ps1
.\examples\manage-api-keys.ps1
```

---

## 📚 More Information

- [Main README](../README.md) - Project overview
- [API Key Security Guide](../docs/API_KEY_SECURITY.md) - Security best practices
- [Feature Implementation Guide](../docs/FEATURE_IMPLEMENTATION_GUIDE.md) - Building features
- [Database Migrations](../docs/DATABASE_MIGRATIONS.md) - Managing database schema
