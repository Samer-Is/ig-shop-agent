# Enhanced IG Shop Agent Test Script
Write-Host "=== Testing Enhanced IG Shop Agent ===" -ForegroundColor Green

$baseUrl = "https://igshop-dev-functions-v2.azurewebsites.net"
$headers = @{"Content-Type" = "application/json"}

# Test 1: Health Check
Write-Host "`n1. Health Check:" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/health" -Headers $headers
    Write-Host "✅ Status: $($health.status)" -ForegroundColor Green
    Write-Host "✅ Version: $($health.version)" -ForegroundColor Green
    Write-Host "✅ AI Agent: $($health.features.ai_agent)" -ForegroundColor Green
    Write-Host "✅ Instagram OAuth: $($health.features.instagram_oauth)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed" -ForegroundColor Red
}

# Test 2: Enhanced Product Catalog
Write-Host "`n2. Enhanced Product Catalog:" -ForegroundColor Yellow
try {
    $catalog = Invoke-RestMethod -Uri "$baseUrl/api/catalog" -Headers $headers
    Write-Host "✅ Total products: $($catalog.total)" -ForegroundColor Green
    Write-Host "✅ Products available:" -ForegroundColor Green
    foreach ($product in $catalog.products) {
        Write-Host "   - $($product.name) ($($product.price) $($product.currency))" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Catalog test failed" -ForegroundColor Red
}

# Test 3: AI Agent - Arabic Message
Write-Host "`n3. AI Agent - Arabic Message:" -ForegroundColor Yellow
try {
    $arabicTest = @{
        message = "مرحبا، أريد أن أشتري قميص"
    } | ConvertTo-Json -Compress
    
    $aiResponse = Invoke-RestMethod -Uri "$baseUrl/api/ai/test-response" -Method POST -Body $arabicTest -ContentType "application/json"
    Write-Host "✅ AI Response: $($aiResponse.ai_response)" -ForegroundColor Green
    Write-Host "✅ Detected Intent: $($aiResponse.detected_intent)" -ForegroundColor Cyan
    Write-Host "✅ Detected Language: $($aiResponse.detected_language)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Arabic AI test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: AI Agent - English Message
Write-Host "`n4. AI Agent - English Message:" -ForegroundColor Yellow
try {
    $englishTest = @{
        message = "Hello, I want to buy a white shirt"
    } | ConvertTo-Json -Compress
    
    $aiResponse = Invoke-RestMethod -Uri "$baseUrl/api/ai/test-response" -Method POST -Body $englishTest -ContentType "application/json"
    Write-Host "✅ AI Response: $($aiResponse.ai_response)" -ForegroundColor Green
    Write-Host "✅ Detected Intent: $($aiResponse.detected_intent)" -ForegroundColor Cyan
    Write-Host "✅ Detected Language: $($aiResponse.detected_language)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ English AI test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Instagram Configuration
Write-Host "`n5. Instagram Configuration:" -ForegroundColor Yellow
try {
    $instaConfig = Invoke-RestMethod -Uri "$baseUrl/api/instagram/config" -Headers $headers
    Write-Host "✅ Instagram App Available: $($instaConfig.available)" -ForegroundColor Green
    Write-Host "✅ App ID: $($instaConfig.app_id)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Instagram config test failed" -ForegroundColor Red
}

# Test 6: Analytics
Write-Host "`n6. Analytics:" -ForegroundColor Yellow
try {
    $analytics = Invoke-RestMethod -Uri "$baseUrl/api/analytics" -Headers $headers
    Write-Host "✅ Total Messages: $($analytics.total_messages)" -ForegroundColor Green
    Write-Host "✅ Total Orders: $($analytics.total_orders)" -ForegroundColor Green
    Write-Host "✅ Response Rate: $($analytics.response_rate)%" -ForegroundColor Green
    Write-Host "✅ Conversion Rate: $($analytics.conversion_rate)%" -ForegroundColor Green
} catch {
    Write-Host "❌ Analytics test failed" -ForegroundColor Red
}

# Test 7: Recent Messages
Write-Host "`n7. Recent Messages:" -ForegroundColor Yellow
try {
    $messages = Invoke-RestMethod -Uri "$baseUrl/api/messages/recent" -Headers $headers
    Write-Host "✅ Total Messages in History: $($messages.total)" -ForegroundColor Green
    Write-Host "✅ Recent Messages Count: $($messages.messages.Count)" -ForegroundColor Green
} catch {
    Write-Host "❌ Recent messages test failed" -ForegroundColor Red
}

# Test 8: Instagram Webhook Verification
Write-Host "`n8. Instagram Webhook:" -ForegroundColor Yellow
try {
    $webhookUrl = "$baseUrl/api/webhook/instagram?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=igshop_webhook_verify_2024"
    $webhookResponse = Invoke-RestMethod -Uri $webhookUrl -Method GET
    Write-Host "✅ Webhook Verification: $webhookResponse" -ForegroundColor Green
} catch {
    Write-Host "❌ Webhook test failed" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "Enhanced IG Shop Agent with AI is ready!" -ForegroundColor Magenta 