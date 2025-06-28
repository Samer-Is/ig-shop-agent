# Simple Backend Test
$baseUrl = "https://igshop-dev-functions-v2.azurewebsites.net/api"

Write-Host "Testing Backend Endpoints" -ForegroundColor Cyan

# Test Health
try {
    $health = Invoke-RestMethod "$baseUrl/health"
    Write-Host "✓ Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Health: Failed" -ForegroundColor Red
}

# Test Catalog
try {
    $catalog = Invoke-RestMethod "$baseUrl/catalog"
    Write-Host "✓ Catalog: $($catalog.products.Count) products" -ForegroundColor Green
} catch {
    Write-Host "✗ Catalog: Failed" -ForegroundColor Red
}

# Test Analytics
try {
    $analytics = Invoke-RestMethod "$baseUrl/analytics"
    Write-Host "✓ Analytics: $($analytics.total_messages) messages" -ForegroundColor Green
} catch {
    Write-Host "✗ Analytics: Failed" -ForegroundColor Red
}

# Test Customers
try {
    $customers = Invoke-RestMethod "$baseUrl/customers"
    Write-Host "✓ Customers: $($customers.total) customers" -ForegroundColor Green
} catch {
    Write-Host "✗ Customers: Failed" -ForegroundColor Red
}

# Test AI
try {
    $body = @{ message = "Hello" } | ConvertTo-Json
    $ai = Invoke-RestMethod "$baseUrl/ai/test-response" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✓ AI: $($ai.detected_language)" -ForegroundColor Green
} catch {
    Write-Host "✗ AI: Failed" -ForegroundColor Red
}

# Test Instagram Status
try {
    $instagram = Invoke-RestMethod "$baseUrl/instagram/status"
    Write-Host "✓ Instagram: Connected=$($instagram.connected)" -ForegroundColor Green
} catch {
    Write-Host "✗ Instagram: Failed" -ForegroundColor Red
}

Write-Host "Backend testing complete!" -ForegroundColor Yellow 