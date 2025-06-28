# Deploy React Dashboard to Azure Static Web App
Write-Host "🚀 Deploying IG Shop Agent React Dashboard..." -ForegroundColor Green

$staticAppName = "red-island-0b863450f"
$resourceGroup = "igshop-dev-rg-v2"  # Adjust if different
$buildPath = "ig-shop-agent-dashboard/dist"

# Check if build exists
if (-not (Test-Path $buildPath)) {
    Write-Host "❌ Build directory not found: $buildPath" -ForegroundColor Red
    Write-Host "The React app needs to be built first." -ForegroundColor Yellow
    Write-Host "Install Node.js and run: cd ig-shop-agent-dashboard && npm install && npm run build" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found build directory: $buildPath" -ForegroundColor Green

# Create deployment zip
$zipPath = "react-dashboard-deploy.zip"
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow

try {
    # Remove old zip if exists
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }

    # Create zip from dist folder
    Compress-Archive -Path "$buildPath/*" -DestinationPath $zipPath -Force
    Write-Host "✅ Created deployment package: $zipPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create deployment package: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Deploy to Azure Static Web App
Write-Host "🌐 Deploying to Azure Static Web App..." -ForegroundColor Yellow
Write-Host "App Name: $staticAppName" -ForegroundColor Cyan

try {
    # Deploy using Azure CLI
    az staticwebapp deploy --name $staticAppName --source $zipPath

    Write-Host "✅ Deployment completed!" -ForegroundColor Green
    Write-Host "🌐 Your dashboard should now be available at:" -ForegroundColor Magenta
    Write-Host "   https://red-island-0b863450f.2.azurestaticapps.net/" -ForegroundColor Cyan
    
    Write-Host "`n🎯 Dashboard Features:" -ForegroundColor Yellow
    Write-Host "  📊 Analytics Dashboard with charts" -ForegroundColor White
    Write-Host "  💬 Conversations management" -ForegroundColor White
    Write-Host "  📦 Orders tracking" -ForegroundColor White
    Write-Host "  🛍️ Product catalog (Arabic/English)" -ForegroundColor White
    Write-Host "  👤 Business profile setup" -ForegroundColor White
    Write-Host "  📚 Knowledge base management" -ForegroundColor White
    Write-Host "  ⚙️ Settings & configuration" -ForegroundColor White
    
    Write-Host "`n🔗 Backend API: https://igshop-dev-functions-v2.azurewebsites.net" -ForegroundColor Magenta

} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try manual upload via Azure Portal" -ForegroundColor Yellow
}

# Cleanup
if (Test-Path $zipPath) {
    Write-Host "🧹 Cleaning up deployment package..." -ForegroundColor Gray
    Remove-Item $zipPath -Force
}

Write-Host "`n🎉 React Dashboard Deployment Complete!" -ForegroundColor Green 