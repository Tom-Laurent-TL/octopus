# FastAPI Testing Script for PowerShell
# This script provides easy commands to test your API endpoints

param(
    [string]$ApiKey = "your-secret-api-key-here",
    [string]$BaseUrl = "http://localhost:8000"
)

Write-Host "FastAPI Testing Helper" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Path,
        [bool]$RequiresAuth = $false,
        [object]$Body = $null
    )
    
    $Uri = "$BaseUrl$Path"
    $params = @{
        Uri = $Uri
        Method = $Method
    }
    
    if ($RequiresAuth) {
        $params.Headers = @{"Octopus-API-Key" = $ApiKey}
    }
    
    if ($Body) {
        $params.Body = ($Body | ConvertTo-Json)
        $params.ContentType = "application/json"
    }
    
    try {
        Write-Host "Testing: $Method $Path" -ForegroundColor Yellow
        $response = Invoke-WebRequest @params
        Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor White
        Write-Host ""
        return $response
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        return $null
    }
}

# Public Endpoints
Write-Host "=== Public Endpoints ===" -ForegroundColor Cyan
Test-Endpoint -Method "GET" -Path "/"
Test-Endpoint -Method "GET" -Path "/health"

# Protected Endpoints (require API key)
Write-Host "=== Protected Endpoints ===" -ForegroundColor Cyan
Test-Endpoint -Method "GET" -Path "/api/v1/users/" -RequiresAuth $true
Test-Endpoint -Method "GET" -Path "/api/v1/conversations/" -RequiresAuth $true

$docsUrl = "$BaseUrl/docs"
Write-Host "Done! For interactive testing, visit: $docsUrl" -ForegroundColor Cyan
