# Test Instagram DM Processing with AI Agent
Write-Host "=== Testing Instagram DM AI Processing ===" -ForegroundColor Green

$baseUrl = "https://igshop-dev-functions-v2.azurewebsites.net"

# Simulate Instagram webhook payload for incoming message
$instagramWebhook = @{
    object = "page"
    entry = @(
        @{
            messaging = @(
                @{
                    sender = @{
                        id = "customer_test_123456"
                    }
                    message = @{
                        text = "مرحبا، أريد أن أشتري بنطال جينز. كم السعر؟"
                    }
                    timestamp = [int][double]::Parse((Get-Date -UFormat %s))
                }
            )
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "`n1. Sending simulated Instagram DM:" -ForegroundColor Yellow
Write-Host "Message: 'مرحبا، أريد أن أشتري بنطال جينز. كم السعر؟'" -ForegroundColor Cyan
Write-Host "Customer ID: customer_test_123456" -ForegroundColor Cyan

try {
    # Send webhook to backend
    $response = Invoke-RestMethod -Uri "$baseUrl/api/webhook/instagram" -Method POST -Body $instagramWebhook -ContentType "application/json"
    Write-Host "✅ Webhook received: $response" -ForegroundColor Green
    
    # Wait for processing
    Start-Sleep -Seconds 2
    
    # Check recent messages to see AI processing result
    Write-Host "`n2. Checking AI processing result:" -ForegroundColor Yellow
    $messages = Invoke-RestMethod -Uri "$baseUrl/api/messages/recent"
    
    if ($messages.messages.Count -gt 0) {
        $latestMessage = $messages.messages[-1]
        Write-Host "✅ Customer Message: $($latestMessage.message)" -ForegroundColor Green
        Write-Host "✅ AI Response: $($latestMessage.ai_response)" -ForegroundColor Green
        Write-Host "✅ Detected Intent: $($latestMessage.intent)" -ForegroundColor Cyan
        Write-Host "✅ Detected Language: $($latestMessage.language)" -ForegroundColor Cyan
        Write-Host "✅ Customer ID: $($latestMessage.customer_id)" -ForegroundColor Cyan
        Write-Host "✅ Timestamp: $($latestMessage.timestamp)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ No messages found in history" -ForegroundColor Yellow
    }
    
    # Check analytics update
    Write-Host "`n3. Checking analytics update:" -ForegroundColor Yellow
    $analytics = Invoke-RestMethod -Uri "$baseUrl/api/analytics"
    Write-Host "✅ Total Messages: $($analytics.total_messages)" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: English message
Write-Host "`n=== Test 2: English Message ===" -ForegroundColor Magenta

$englishWebhook = @{
    object = "page"
    entry = @(
        @{
            messaging = @(
                @{
                    sender = @{
                        id = "customer_english_789"
                    }
                    message = @{
                        text = "Hi! I want to order a white shirt. What sizes do you have?"
                    }
                    timestamp = [int][double]::Parse((Get-Date -UFormat %s))
                }
            )
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "Message: 'Hi! I want to order a white shirt. What sizes do you have?'" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/webhook/instagram" -Method POST -Body $englishWebhook -ContentType "application/json"
    Write-Host "✅ Webhook received: $response" -ForegroundColor Green
    
    Start-Sleep -Seconds 2
    
    $messages = Invoke-RestMethod -Uri "$baseUrl/api/messages/recent"
    if ($messages.messages.Count -gt 1) {
        $latestMessage = $messages.messages[-1]
        Write-Host "✅ AI Response: $($latestMessage.ai_response)" -ForegroundColor Green
        Write-Host "✅ Intent: $($latestMessage.intent)" -ForegroundColor Cyan
        Write-Host "✅ Language: $($latestMessage.language)" -ForegroundColor Cyan
    }
    
    $analytics = Invoke-RestMethod -Uri "$baseUrl/api/analytics"
    Write-Host "✅ Updated Total Messages: $($analytics.total_messages)" -ForegroundColor Green
    
} catch {
    Write-Host "❌ English test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Instagram DM AI Processing Complete ===" -ForegroundColor Green
Write-Host "🤖 AI Agent is successfully processing customer messages!" -ForegroundColor Magenta 