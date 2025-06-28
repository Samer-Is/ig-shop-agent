#!/usr/bin/env pwsh

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "COMPREHENSIVE AZURE FUNCTIONS PYTHON FIX" -ForegroundColor Cyan  
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$ResourceGroup = "igshop-dev-rg-v2"
$FunctionAppName = "igshop-dev-functions-v2"

# Step 1: Stop the Function App
Write-Host "Step 1: Stopping Function App..." -ForegroundColor Yellow
az functionapp stop --resource-group $ResourceGroup --name $FunctionAppName

# Step 2: Clear all app settings that might cause conflicts
Write-Host "Step 2: Clearing conflicting app settings..." -ForegroundColor Yellow
az functionapp config appsettings delete --resource-group $ResourceGroup --name $FunctionAppName --setting-names "WEBSITE_RUN_FROM_PACKAGE" "SCM_DO_BUILD_DURING_DEPLOYMENT" "WEBSITE_NODE_DEFAULT_VERSION"

# Step 3: Set correct Python runtime settings
Write-Host "Step 3: Setting Python runtime..." -ForegroundColor Yellow
az functionapp config appsettings set --resource-group $ResourceGroup --name $FunctionAppName --settings `
    "FUNCTIONS_WORKER_RUNTIME=python" `
    "FUNCTIONS_EXTENSION_VERSION=~4" `
    "PYTHONPATH=/home/site/wwwroot" `
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
    "AzureWebJobsFeatureFlags=EnableWorkerIndexing"

# Step 4: Set the correct Linux FX Version
Write-Host "Step 4: Setting Linux runtime version..." -ForegroundColor Yellow
az functionapp config set --resource-group $ResourceGroup --name $FunctionAppName --linux-fx-version "Python|3.11"

# Step 5: Create clean deployment package
Write-Host "Step 5: Creating clean deployment package..." -ForegroundColor Yellow
Set-Location backend
Remove-Item "../backend-fixed-final.zip" -ErrorAction SilentlyContinue
Compress-Archive -Path "function_app.py","host.json","requirements.txt",".funcignore" -DestinationPath "../backend-fixed-final.zip" -Force

# Step 6: Deploy with build-remote
Write-Host "Step 6: Deploying Python functions..." -ForegroundColor Yellow
az functionapp deployment source config-zip --resource-group $ResourceGroup --name $FunctionAppName --src "../backend-fixed-final.zip" --build-remote true

# Step 7: Start the Function App
Write-Host "Step 7: Starting Function App..." -ForegroundColor Yellow
az functionapp start --resource-group $ResourceGroup --name $FunctionAppName

# Step 8: Wait for startup
Write-Host "Step 8: Waiting for startup..." -ForegroundColor Yellow
Start-Sleep 45

# Step 9: Test the deployment
Write-Host "Step 9: Testing deployment..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Testing: https://igshop-dev-functions-v2.azurewebsites.net/api/health" -ForegroundColor Green

try {
    $response = Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/health" -Method Get -TimeoutSec 20
    Write-Host "SUCCESS! Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Checking Function App status..." -ForegroundColor Yellow
    az functionapp show --resource-group $ResourceGroup --name $FunctionAppName --query "{state: state, runtime: linuxFxVersion}" --output table
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan 