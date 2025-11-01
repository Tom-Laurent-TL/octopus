# Test Scripts

This folder contains PowerShell test scripts for the FastAPI application.

## Scripts

### `test-api.ps1`

Tests basic API functionality including authentication, user endpoints, and protected routes.

**Usage:**
```powershell
.\scripts\test-api.ps1
```

**Features:**
- Tests public endpoints (root, health)
- Tests authentication (valid/invalid API keys)
- Tests protected endpoints (users, items, admin)
- Color-coded output for easy reading

**Customization:**
Edit the variables at the top of the script:
```powershell
$baseUrl = "http://localhost:8000/api/v1"
$apiKey = "your-secret-api-key-here"
```

### `test-conversations.ps1`

Comprehensive test of the many-to-many conversation system with user tracking.

**Usage:**
```powershell
.\scripts\test-conversations.ps1
```

**Features:**
- Creates or fetches existing users
- Creates conversations with multiple participants
- Adds messages with user_id tracking
- Tests participant management (add/remove)
- Lists user-specific conversations
- Full end-to-end workflow demonstration

**What it tests:**
1. User creation/retrieval
2. Conversation creation with participants
3. Message posting with sender tracking
4. Dynamic participant management
5. User conversation listing
6. Participant removal

**Output:**
Shows detailed progress with color-coded messages:
- Green: Successful operations
- Yellow: Using existing resources
- Gray: Detailed information

## Requirements

- PowerShell 5.1 or higher
- FastAPI server running on http://localhost:8000
- Valid API key configured in `.env` file

## Notes

- Scripts handle existing users gracefully (won't fail if users already exist)
- All operations require a valid API key
- Scripts use the API configured in `.env` file
