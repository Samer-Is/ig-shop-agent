# Run Professional React Dashboard Locally
Write-Host "🚀 Starting Professional IG Shop Agent Dashboard..." -ForegroundColor Green

$dashboardPath = "ig-shop-agent-dashboard/dist"

# Check if built dashboard exists
if (-not (Test-Path $dashboardPath)) {
    Write-Host "❌ React dashboard not found at: $dashboardPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found React dashboard build" -ForegroundColor Green

# Navigate to dashboard directory
Set-Location $dashboardPath

Write-Host "`n🌐 Starting Professional Dashboard Server..." -ForegroundColor Yellow
Write-Host "📱 Dashboard will be available at: http://localhost:8080" -ForegroundColor Magenta
Write-Host "🔗 Backend API: https://igshop-dev-functions-v2.azurewebsites.net" -ForegroundColor Magenta

Write-Host "`n🎯 PROFESSIONAL FEATURES:" -ForegroundColor Cyan
Write-Host "  📊 Analytics Dashboard - Charts, KPIs, revenue tracking" -ForegroundColor White
Write-Host "  💬 Conversations - Real-time Instagram DM management" -ForegroundColor White
Write-Host "  📦 Orders - Complete order tracking system" -ForegroundColor White
Write-Host "  🛍️ Product Catalog - Full CRUD with Arabic/English" -ForegroundColor White
Write-Host "  👤 Business Profile - Instagram integration settings" -ForegroundColor White
Write-Host "  📚 Knowledge Base - AI training data management" -ForegroundColor White
Write-Host "  ⚙️ Settings - Complete configuration system" -ForegroundColor White

Write-Host "`n⚡ Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Green

try {
    # Start Python HTTP server on port 8080
    python -m http.server 8080
} catch {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
    Write-Host "💡 Make sure Python is installed" -ForegroundColor Yellow
}

# Return to original directory
Set-Location ../..
Write-Host "`n✅ Professional Dashboard stopped" -ForegroundColor Green 