#!/usr/bin/env pwsh
# Test Backend API Endpoints

$baseUrl = "https://igshop-dev-yjhtoi-api.azurewebsites.net"

Write-Host "Testing IG-Shop-Agent Backend API..." -ForegroundColor Green
Write-Host "Base URL: $baseUrl" -ForegroundColor Cyan

# Test endpoints
$endpoints = @(
    @{Path = "/"; Name = "Root"},
    @{Path = "/health"; Name = "Health Check"},
    @{Path = "/api/health"; Name = "API Health"},
    @{Path = "/webhook/instagram?hub.mode=subscribe`&hub.challenge=test123`&hub.verify_token=ig_shop_webhook_verify_123"; Name = "Instagram Webhook Verification"}
)

foreach ($endpoint in $endpoints) {
    Write-Host "`n--- Testing $($endpoint.Name) ---" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl$($endpoint.Path)" -Method Get -TimeoutSec 10
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "❌ FAILED - Status: $statusCode" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nBackend testing complete!" -ForegroundColor Green 