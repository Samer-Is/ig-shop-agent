# Azure Web App Configuration Script for IG-Shop-Agent
# Run this if GitHub Actions deployment has issues

# Set variables
$resourceGroup = "igshop-dev-rg-v2"
$webAppName = "igshop-dev-yjhtoi-api"

Write-Host "Configuring Azure Web App: $webAppName" -ForegroundColor Green

# Configure Python runtime
Write-Host "Setting Python 3.11 runtime..." -ForegroundColor Yellow
az webapp config set `
  --resource-group $resourceGroup `
  --name $webAppName `
  --linux-fx-version "PYTHON|3.11"

# Configure startup command
Write-Host "Setting startup command..." -ForegroundColor Yellow
az webapp config set `
  --resource-group $resourceGroup `
  --name $webAppName `
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app_azure:app"

# Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $webAppName `
  --settings `
    META_APP_ID="1879578119651644" `
    META_APP_SECRET="f79b3350f43751d6139e1b29a232cbf3" `
    OPENAI_API_KEY="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" `
    JWT_SECRET_KEY="secure-jwt-key-2024" `
    META_REDIRECT_URI="https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback" `
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Restart the web app
Write-Host "Restarting web app..." -ForegroundColor Yellow
az webapp restart --resource-group $resourceGroup --name $webAppName

Write-Host "Configuration complete! Testing endpoints..." -ForegroundColor Green

# Test the endpoints
Start-Sleep -Seconds 30
$healthUrl = "https://$webAppName.azurewebsites.net/health"
$mainUrl = "https://$webAppName.azurewebsites.net/"

Write-Host "Testing health endpoint: $healthUrl" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing
    Write-Host "✅ Health check: $($response.StatusCode)" -ForegroundColor Green
    Write-Host $response.Content
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Testing main endpoint: $mainUrl" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri $mainUrl -UseBasicParsing
    Write-Host "✅ Main endpoint: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Main endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Azure Web App configuration completed!" -ForegroundColor Green 