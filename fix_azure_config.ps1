# Fix Azure Web App Configuration for IG-Shop-Agent
Write-Host "🔧 Fixing Azure Web App Configuration..." -ForegroundColor Green

# Set the startup command for Flask app
Write-Host "Setting startup command..." -ForegroundColor Yellow
az webapp config set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 production_app:app"

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --settings `
    META_APP_ID="1879578119651644" `
    META_APP_SECRET="f79b3350f43751d6139e1b29a232cbf3" `
    OPENAI_API_KEY="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" `
    JWT_SECRET_KEY="production-secret-key-change-in-prod" `
    META_REDIRECT_URI="https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback" `
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Restart the app to apply changes
Write-Host "Restarting app..." -ForegroundColor Yellow
az webapp restart --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api

Write-Host "✅ Configuration updated! Waiting for app to restart..." -ForegroundColor Green
Start-Sleep -Seconds 30

# Test the health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "https://igshop-dev-yjhtoi-api.azurewebsites.net/health" -Method GET -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 200) {
    Write-Host "✅ Backend is responding correctly!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Cyan
} else {
    Write-Host "❌ Backend still not responding. Status: $($response.StatusCode)" -ForegroundColor Red
}

Write-Host "🌐 Frontend URL: https://red-island-0b863450f.2.azurestaticapps.net" -ForegroundColor Cyan
Write-Host "🔗 Backend URL: https://igshop-dev-yjhtoi-api.azurewebsites.net" -ForegroundColor Cyan 