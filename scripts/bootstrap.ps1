# Bootstrap script to initialize the Octopus API with a master API key
# This script calls the /bootstrap endpoint to create the initial master key

$baseUrl = "http://localhost:8000"

Write-Host "`n=== Octopus API Bootstrap ===" -ForegroundColor Cyan
Write-Host "This will create the master API key for your application.`n"

# Check if server is running
try {
    $healthCheck = Invoke-WebRequest -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    Write-Host "Server is running" -ForegroundColor Green
}
catch {
    Write-Host "Server is not running!" -ForegroundColor Red
    Write-Host "Please start the server first:" -ForegroundColor Yellow
    Write-Host "  uv run fastapi dev app/main.py`n" -ForegroundColor Yellow
    exit 1
}

# Call the bootstrap endpoint
Write-Host "`nCreating master API key..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/bootstrap" -Method Post -ContentType "application/json"
    
    Write-Host "`nSUCCESS! Master API Key Created" -ForegroundColor Green
    Write-Host "API Key: $($response.api_key)" -ForegroundColor Yellow
    Write-Host "Name: $($response.name)"
    Write-Host "Scopes: $($response.scopes)"
    
    Write-Host "`nIMPORTANT: Save this API key securely!" -ForegroundColor Yellow
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Add to .env file: MASTER_API_KEY=$($response.api_key)" -ForegroundColor Gray
    Write-Host "2. Use header: Octopus-API-Key = $($response.api_key)" -ForegroundColor Gray
    Write-Host "3. See docs/API_KEY_MANAGEMENT.md for more info" -ForegroundColor Gray
    Write-Host ""
}
catch {
    $errorMessage = $_.Exception.Message
    if ($errorMessage -like "*400*") {
        Write-Host "`nBootstrap already completed!" -ForegroundColor Yellow
        Write-Host "Use your existing master key.`n" -ForegroundColor Yellow
    }
    else {
        Write-Host "`nBootstrap failed!" -ForegroundColor Red
        Write-Host "Error: $errorMessage" -ForegroundColor Red
    }
    exit 1
}
