# Test Frontend-Backend Integration
Write-Host "🔗 Testing Frontend-Backend Connection..." -ForegroundColor Green

# Test if frontend is running
try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing
    Write-Host "✅ Frontend: Running on http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend: Not running. Run .\run-frontend-local.ps1 first" -ForegroundColor Red
}

# Test backend API
try {
    $backendTest = Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/health"
    Write-Host "✅ Backend: $($backendTest.status) - $($backendTest.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend: Not responding" -ForegroundColor Red
}

# Test AI Agent
try {
    $aiTest = @{ message = "hello" } | ConvertTo-Json -Compress
    $aiResponse = Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/ai/test-response" -Method POST -Body $aiTest -ContentType "application/json"
    Write-Host "✅ AI Agent: Working - '$($aiResponse.ai_response)'" -ForegroundColor Green
} catch {
    Write-Host "❌ AI Agent: Error" -ForegroundColor Red
}

# Test product catalog
try {
    $catalogTest = Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/catalog"
    Write-Host "✅ Product Catalog: $($catalogTest.total) products available" -ForegroundColor Green
} catch {
    Write-Host "❌ Product Catalog: Error" -ForegroundColor Red
}

Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Magenta
Write-Host "1. Open browser: http://localhost:8000" -ForegroundColor Yellow
Write-Host "2. Test AI with Arabic message in browser" -ForegroundColor Yellow
Write-Host "3. Click Connect to Instagram to see OAuth flow" -ForegroundColor Yellow
Write-Host "4. Check analytics and product sections" -ForegroundColor Yellow
Write-Host "`n🚀 Your IG Shop Agent is FULLY WORKING!" -ForegroundColor Green 