#!/usr/bin/env pwsh

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "IG SHOP AGENT VERIFICATION TESTS" -ForegroundColor Cyan  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "https://igshop-dev-functions-v2.azurewebsites.net"

# Test 1: Health Check
Write-Host "TEST 1: Health Check" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS - Status: $($health.status)" -ForegroundColor Green
    Write-Host "Message: $($health.message)" -ForegroundColor White
    Write-Host "Timestamp: $($health.timestamp)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Product Catalog
Write-Host "TEST 2: Product Catalog" -ForegroundColor Yellow
try {
    $catalog = Invoke-RestMethod -Uri "$BaseUrl/api/catalog" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS - Found $($catalog.products.Count) products" -ForegroundColor Green
    foreach ($product in $catalog.products) {
        Write-Host "  - $($product.name) ($($product.price) $($product.currency))" -ForegroundColor White
    }
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Auth Login
Write-Host "TEST 3: Auth Login" -ForegroundColor Yellow
try {
    $authBody = '{"email":"test@igshop.com","password":"testpass123"}'
    $authHeaders = @{"Content-Type" = "application/json"}
    $auth = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method Post -Body $authBody -Headers $authHeaders -TimeoutSec 10
    Write-Host "✅ SUCCESS - Token received" -ForegroundColor Green
    Write-Host "User: $($auth.user.email)" -ForegroundColor White
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Instagram Webhook Verification
Write-Host "TEST 4: Instagram Webhook Verification" -ForegroundColor Yellow
try {
    $webhookUrl = "$BaseUrl/api/webhook/instagram?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=igshop_webhook_verify_2024"
    $challenge = Invoke-RestMethod -Uri $webhookUrl -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS - Challenge: $challenge" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Root endpoint
Write-Host "TEST 5: Root API Info" -ForegroundColor Yellow
try {
    $root = Invoke-RestMethod -Uri "$BaseUrl/api/" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS - API: $($root.message)" -ForegroundColor Green
    Write-Host "Available endpoints:" -ForegroundColor White
    foreach ($endpoint in $root.endpoints.PSObject.Properties) {
        Write-Host "  - $($endpoint.Name): $($endpoint.Value)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan 