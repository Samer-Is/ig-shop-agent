# Run IG Shop Agent Frontend Locally
Write-Host "🚀 Starting IG Shop Agent Frontend..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Python not found. Please install Python from https://python.org" -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
if (Test-Path "frontend") {
    Set-Location "frontend"
    Write-Host "✅ Frontend directory found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend directory not found" -ForegroundColor Red
    exit 1
}

# Start local HTTP server
Write-Host "`n🌐 Starting local web server..." -ForegroundColor Yellow
Write-Host "📱 Frontend will be available at: http://localhost:8000" -ForegroundColor Magenta
Write-Host "🔗 Backend API: https://igshop-dev-functions-v2.azurewebsites.net" -ForegroundColor Magenta
Write-Host "`n⚡ Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Green

try {
    # Start Python HTTP server
    python -m http.server 8000
} catch {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
}

# Return to original directory
Set-Location .. 