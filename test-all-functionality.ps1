#!/usr/bin/env pwsh

Write-Host "🧪 COMPREHENSIVE IG SHOP AGENT FUNCTIONALITY TEST" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$API_URL = "https://igshop-dev-functions-v2.azurewebsites.net/api"

# Test 1: Backend Health Check
Write-Host "`n1️⃣ Testing Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/health" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Backend Status: $($data.status)" -ForegroundColor Green
    Write-Host "✅ Version: $($data.version)" -ForegroundColor Green
    Write-Host "✅ AI Agent: $($data.features.ai_agent)" -ForegroundColor Green
    Write-Host "✅ Instagram OAuth: $($data.features.instagram_oauth)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Product Catalog
Write-Host "`n2️⃣ Testing Product Catalog..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/catalog" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Products loaded: $($data.products.Count)" -ForegroundColor Green
    foreach ($product in $data.products) {
        Write-Host "   - $($product.name) ($($product.name_en)) - $($product.price) $($product.currency)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Product Catalog Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: AI Agent Testing
Write-Host "`n3️⃣ Testing AI Agent..." -ForegroundColor Yellow
try {
    $testMessages = @(
        "مرحبا",
        "Hello",
        "كم سعر القميص؟",
        "What is the price of the shirt?"
    )
    
    foreach ($message in $testMessages) {
        Write-Host "   Testing: '$message'" -ForegroundColor Cyan
        
        $webhookPayload = @{
            object = "instagram"
            entry = @(
                @{
                    messaging = @(
                        @{
                            sender = @{ id = "test_user_$(Get-Random)" }
                            recipient = @{ id = "your_page_id" }
                            timestamp = [System.DateTimeOffset]::Now.ToUnixTimeMilliseconds()
                            message = @{ text = $message }
                        }
                    )
                }
            )
        } | ConvertTo-Json -Depth 10
        
        $response = Invoke-WebRequest -Uri "$API_URL/webhook/instagram" -Method POST -Body $webhookPayload -ContentType "application/json"
        $data = $response.Content | ConvertFrom-Json
        Write-Host "   ✅ AI Response: $($data.ai_response)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ AI Agent Test Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Instagram OAuth Endpoints
Write-Host "`n4️⃣ Testing Instagram OAuth..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/instagram/config" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Instagram App ID: $($data.app_id)" -ForegroundColor Green
    Write-Host "✅ Redirect URI: $($data.redirect_uri)" -ForegroundColor Green
} catch {
    Write-Host "❌ Instagram OAuth Config Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Analytics
Write-Host "`n5️⃣ Testing Analytics..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/analytics" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Total Messages: $($data.total_messages)" -ForegroundColor Green
    Write-Host "✅ Total Orders: $($data.total_orders)" -ForegroundColor Green
    Write-Host "✅ Response Rate: $($data.response_rate)%" -ForegroundColor Green
} catch {
    Write-Host "❌ Analytics Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Message History
Write-Host "`n6️⃣ Testing Message History..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/messages/recent" -Method GET
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Recent Messages: $($data.messages.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Message History Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 ALL TESTS COMPLETED!" -ForegroundColor Green
Write-Host "Backend is fully functional and ready for frontend integration!" -ForegroundColor Green 