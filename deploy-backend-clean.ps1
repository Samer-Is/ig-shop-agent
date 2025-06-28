#!/usr/bin/env pwsh

# Deploy Backend to Azure Functions
$functionAppName = "igshop-dev-functions-v2"
$resourceGroup = "igshop-dev-rg-v2"

Write-Host "🚀 Deploying IG-Shop-Agent Backend..." -ForegroundColor Green

# Change to backend directory
Push-Location backend

try {
    Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
    
    # Create a clean zip package
    $tempDir = "../temp-backend-deploy"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    # Copy only the files we need
    Copy-Item "function_app.py" "$tempDir/"
    Copy-Item "requirements.txt" "$tempDir/"
    Copy-Item "host.json" "$tempDir/"
    Copy-Item ".funcignore" "$tempDir/" -ErrorAction SilentlyContinue
    
    # Create deployment zip
    $zipPath = "../backend-clean-deploy.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Push-Location $tempDir
    Compress-Archive -Path "*" -DestinationPath "../backend-clean-deploy.zip" -Force
    Pop-Location
    
    Write-Host "✅ Package created: backend-clean-deploy.zip" -ForegroundColor Green
    
    Write-Host "🔄 Deploying to Azure..." -ForegroundColor Yellow
    
    # Deploy to Azure Function App
    az functionapp deployment source config-zip `
        --resource-group $resourceGroup `
        --name $functionAppName `
        --src "backend-clean-deploy.zip" `
        --build-remote true
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
        Write-Host "🔗 Function App URL: https://$functionAppName.azurewebsites.net" -ForegroundColor Cyan
        
        Write-Host "🔧 Enabling HTTP logging..." -ForegroundColor Yellow
        
        # Enable HTTP logging
        az functionapp config appsettings set `
            --resource-group $resourceGroup `
            --name $functionAppName `
            --settings "AzureWebJobsFeatureFlags=EnableWorkerIndexing" "FUNCTIONS_WORKER_RUNTIME=python"
            
        az functionapp log config `
            --resource-group $resourceGroup `
            --name $functionAppName `
            --application-logging filesystem `
            --web-server-logging filesystem
            
        Write-Host "✅ HTTP logging enabled!" -ForegroundColor Green
        
        Write-Host "🧪 Testing endpoints..." -ForegroundColor Yellow
        
        # Wait a moment for deployment to complete
        Start-Sleep 10
        
        # Test the health endpoint
        $healthUrl = "https://$functionAppName.azurewebsites.net/api/health"
        Write-Host "Testing: $healthUrl" -ForegroundColor Cyan
        
        try {
            $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 30
            Write-Host "✅ Health check passed!" -ForegroundColor Green
            Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
        }
        catch {
            Write-Host "⚠️ Health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "This is normal immediately after deployment. Try again in a few minutes." -ForegroundColor Gray
        }
    }
    else {
        Write-Host "❌ Deployment failed!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
    
    # Clean up temp files
    if (Test-Path "../temp-backend-deploy") {
        Remove-Item "../temp-backend-deploy" -Recurse -Force
    }
}

Write-Host ""
Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host "📊 To view logs, go to:" -ForegroundColor Cyan
Write-Host "   Azure Portal → Function App → Monitoring → Log stream" -ForegroundColor Gray
Write-Host ""
Write-Host "🔗 Available endpoints:" -ForegroundColor Cyan
Write-Host "   Health: https://$functionAppName.azurewebsites.net/api/health" -ForegroundColor Gray
Write-Host "   Root:   https://$functionAppName.azurewebsites.net/api/" -ForegroundColor Gray
Write-Host "   Login:  https://$functionAppName.azurewebsites.net/api/auth/login" -ForegroundColor Gray
Write-Host "   Catalog: https://$functionAppName.azurewebsites.net/api/catalog" -ForegroundColor Gray