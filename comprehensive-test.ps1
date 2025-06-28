#!/usr/bin/env pwsh

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "COMPREHENSIVE IG SHOP AGENT TESTING" -ForegroundColor Cyan  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "https://igshop-dev-functions-v2.azurewebsites.net"

# Test 1: Health Check
Write-Host "TEST 1: Health Check" -ForegroundColor Yellow
Write-Host "URL: $BaseUrl/api/health" -ForegroundColor Gray
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $health | ConvertTo-Json | Write-Host
    Write-Host ""
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 2: Product Catalog
Write-Host "TEST 2: Product Catalog (Arabic Products)" -ForegroundColor Yellow
Write-Host "URL: $BaseUrl/api/catalog" -ForegroundColor Gray
try {
    $catalog = Invoke-RestMethod -Uri "$BaseUrl/api/catalog" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $catalog | ConvertTo-Json -Depth 4 | Write-Host
    Write-Host ""
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 3: Auth Login (POST with JSON)
Write-Host "TEST 3: Auth Login" -ForegroundColor Yellow
Write-Host "URL: $BaseUrl/api/auth/login" -ForegroundColor Gray
try {
    $authBody = @{
        email = "test@igshop.com"
        password = "testpass123"
    } | ConvertTo-Json
    
    $authHeaders = @{
        "Content-Type" = "application/json"
    }
    
    $auth = Invoke-RestMethod -Uri "$BaseUrl/api/auth/login" -Method Post -Body $authBody -Headers $authHeaders -TimeoutSec 10
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $auth | ConvertTo-Json -Depth 3 | Write-Host
    Write-Host ""
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 4: Instagram Webhook Verification
Write-Host "TEST 4: Instagram Webhook Verification" -ForegroundColor Yellow
Write-Host "URL: $BaseUrl/api/webhook/instagram" -ForegroundColor Gray
try {
    $webhookUrl = "$BaseUrl/api/webhook/instagram?hub.mode=subscribe&hub.challenge=test_challenge_123&hub.verify_token=igshop_webhook_verify_2024"
    $webhook = Invoke-RestMethod -Uri $webhookUrl -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Challenge Response: $webhook" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 5: Instagram Webhook POST (Simulate Instagram message)
Write-Host "TEST 5: Instagram Webhook POST (Simulated Message)" -ForegroundColor Yellow
Write-Host "URL: $BaseUrl/api/webhook/instagram" -ForegroundColor Gray
try {
    $instagramMessage = @{
        object = "page"
        entry = @(
            @{
                id = "page_id_123"
                time = 1672531200
                messaging = @(
                    @{
                        sender = @{ id = "user_123" }
                        recipient = @{ id = "page_123" }
                        timestamp = 1672531200
                        message = @{
                            mid = "msg_123"
                            text = "مرحبا، أريد أن أرى المنتجات"
                        }
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 5
    
    $webhookHeaders = @{
        "Content-Type" = "application/json"
    }
    
    $webhookPost = Invoke-RestMethod -Uri "$BaseUrl/api/webhook/instagram" -Method Post -Body $instagramMessage -Headers $webhookHeaders -TimeoutSec 10
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Webhook processed successfully" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test 6: Root endpoint
Write-Host "TEST 6: Root API Endpoint" -ForegroundColor Yellow
Write-Host "URL: $BaseUrl/api/" -ForegroundColor Gray
try {
    $root = Invoke-RestMethod -Uri "$BaseUrl/api/" -Method Get -TimeoutSec 10
    Write-Host "✅ SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $root | ConvertTo-Json -Depth 3 | Write-Host
    Write-Host ""
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "TESTING COMPLETE" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan 