# Script to manage API keys via the Octopus API
# Usage examples at the bottom of this file

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey = $env:MASTER_API_KEY,
    
    [Parameter(Mandatory=$false)]
    [string]$BaseUrl = "http://localhost:8000"
)

# Check if API key is provided
if (-not $ApiKey) {
    Write-Host "Error: API key not provided!" -ForegroundColor Red
    Write-Host "Set the MASTER_API_KEY environment variable or pass -ApiKey parameter`n" -ForegroundColor Yellow
    exit 1
}

$headers = @{
    "Octopus-API-Key" = $ApiKey
    "Content-Type" = "application/json"
}

function Show-Menu {
    Write-Host "`n=== Octopus API Key Management ===" -ForegroundColor Cyan
    Write-Host "1. List all API keys" -ForegroundColor White
    Write-Host "2. Create new API key" -ForegroundColor White
    Write-Host "3. Get API key details" -ForegroundColor White
    Write-Host "4. Update API key" -ForegroundColor White
    Write-Host "5. Deactivate API key" -ForegroundColor White
    Write-Host "6. Delete API key" -ForegroundColor White
    Write-Host "Q. Quit" -ForegroundColor White
    Write-Host ""
}

function List-ApiKeys {
    Write-Host "`nFetching API keys..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/api-keys/" -Method Get -Headers $headers
        
        if ($response.Count -eq 0) {
            Write-Host "No API keys found." -ForegroundColor Yellow
            return
        }
        
        Write-Host "`nFound $($response.Count) API key(s):`n" -ForegroundColor Green
        
        $response | ForEach-Object {
            Write-Host "ID: $($_.id)" -ForegroundColor Cyan
            Write-Host "  Name: $($_.name)"
            Write-Host "  Scopes: $($_.scopes)"
            Write-Host "  Active: $($_.is_active)"
            Write-Host "  Created: $($_.created_at)"
            Write-Host "  Last Used: $($_.last_used_at)"
            if ($_.expires_at) {
                Write-Host "  Expires: $($_.expires_at)" -ForegroundColor Yellow
            }
            Write-Host ""
        }
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Create-ApiKey {
    Write-Host "`n=== Create New API Key ===" -ForegroundColor Cyan
    
    $name = Read-Host "Enter key name"
    $description = Read-Host "Enter description (optional)"
    $scopes = Read-Host "Enter scopes (read,write,admin) [default: read]"
    $daysToExpire = Read-Host "Expire in how many days? (leave empty for no expiration)"
    
    if (-not $scopes) {
        $scopes = "read"
    }
    
    $body = @{
        name = $name
        scopes = $scopes
    }
    
    if ($description) {
        $body.description = $description
    }
    
    if ($daysToExpire) {
        $expiresAt = (Get-Date).AddDays([int]$daysToExpire).ToString("o")
        $body.expires_at = $expiresAt
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/api-keys/" -Method Post -Headers $headers -Body ($body | ConvertTo-Json)
        
        Write-Host "`n" + "=" * 70 -ForegroundColor Green
        Write-Host "SUCCESS! API Key Created" -ForegroundColor Green
        Write-Host "=" * 70 -ForegroundColor Green
        
        Write-Host "`nAPI Key: " -NoNewline -ForegroundColor Cyan
        Write-Host $response.key -ForegroundColor Yellow
        
        Write-Host "Name: " -NoNewline -ForegroundColor Cyan
        Write-Host $response.name
        
        Write-Host "Scopes: " -NoNewline -ForegroundColor Cyan
        Write-Host $response.scopes
        
        Write-Host "`nIMPORTANT: Save this key securely! It won't be shown again.`n" -ForegroundColor Yellow
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Get-ApiKeyDetails {
    $keyId = Read-Host "`nEnter API key ID"
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/api-keys/$keyId" -Method Get -Headers $headers
        
        Write-Host "`nAPI Key Details:" -ForegroundColor Cyan
        Write-Host "ID: $($response.id)"
        Write-Host "Name: $($response.name)"
        Write-Host "Description: $($response.description)"
        Write-Host "Scopes: $($response.scopes)"
        Write-Host "Active: $($response.is_active)"
        Write-Host "Created: $($response.created_at)"
        Write-Host "Last Used: $($response.last_used_at)"
        if ($response.expires_at) {
            Write-Host "Expires: $($response.expires_at)"
        }
        Write-Host ""
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Update-ApiKey {
    $keyId = Read-Host "`nEnter API key ID"
    
    Write-Host "Leave fields empty to keep current value" -ForegroundColor Gray
    $name = Read-Host "New name (optional)"
    $description = Read-Host "New description (optional)"
    $scopes = Read-Host "New scopes (optional)"
    $isActive = Read-Host "Active? (true/false, optional)"
    
    $body = @{}
    
    if ($name) { $body.name = $name }
    if ($description) { $body.description = $description }
    if ($scopes) { $body.scopes = $scopes }
    if ($isActive) { $body.is_active = [System.Convert]::ToBoolean($isActive) }
    
    if ($body.Count -eq 0) {
        Write-Host "No changes specified." -ForegroundColor Yellow
        return
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/api-keys/$keyId" -Method Patch -Headers $headers -Body ($body | ConvertTo-Json)
        
        Write-Host "`nAPI key updated successfully!" -ForegroundColor Green
        Write-Host "Name: $($response.name)"
        Write-Host "Scopes: $($response.scopes)"
        Write-Host "Active: $($response.is_active)`n"
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Deactivate-ApiKey {
    $keyId = Read-Host "`nEnter API key ID to deactivate"
    
    $confirm = Read-Host "Are you sure you want to deactivate this key? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        return
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/v1/api-keys/$keyId/deactivate" -Method Post -Headers $headers
        
        Write-Host "`nAPI key deactivated successfully!" -ForegroundColor Green
        Write-Host "The key can no longer be used for authentication.`n"
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Delete-ApiKey {
    $keyId = Read-Host "`nEnter API key ID to DELETE"
    
    Write-Host "WARNING: This will permanently delete the API key!" -ForegroundColor Red
    $confirm = Read-Host "Type 'DELETE' to confirm"
    
    if ($confirm -ne "DELETE") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        return
    }
    
    try {
        Invoke-RestMethod -Uri "$BaseUrl/api/v1/api-keys/$keyId" -Method Delete -Headers $headers
        
        Write-Host "`nAPI key deleted successfully!`n" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main menu loop
do {
    Show-Menu
    $choice = Read-Host "Select an option"
    
    switch ($choice) {
        "1" { List-ApiKeys }
        "2" { Create-ApiKey }
        "3" { Get-ApiKeyDetails }
        "4" { Update-ApiKey }
        "5" { Deactivate-ApiKey }
        "6" { Delete-ApiKey }
        "Q" { Write-Host "`nGoodbye!`n" -ForegroundColor Cyan }
        default { Write-Host "Invalid option" -ForegroundColor Red }
    }
} while ($choice -ne "Q")

<#
.SYNOPSIS
    Manage Octopus API keys via the REST API

.DESCRIPTION
    Interactive menu for managing API keys:
    - List all keys
    - Create new keys with custom scopes
    - Update existing keys
    - Deactivate or delete keys

.PARAMETER ApiKey
    Your master API key with admin scope. Can also be set via API_KEY environment variable.

.PARAMETER BaseUrl
    Base URL of the API. Defaults to http://localhost:8000

.EXAMPLE
    # Use API key from environment variable
    $env:MASTER_API_KEY = "your-master-key"
    .\manage-api-keys.ps1

.EXAMPLE
    # Pass API key as parameter
    .\manage-api-keys.ps1 -ApiKey "your-master-key"

.EXAMPLE
    # Use custom base URL
    .\manage-api-keys.ps1 -BaseUrl "https://api.example.com"
#>
