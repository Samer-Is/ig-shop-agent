#!/usr/bin/env pwsh
# Deploy Backend to Azure Functions
# This script deploys the FastAPI backend to Azure Functions

param(
    [string]$ResourceGroup = "igshop-dev-yjhtoi",
    [string]$FunctionAppName = "igshop-dev-yjhtoi-api",
    [string]$Region = "eastus"
)

Write-Host "🚀 Deploying IG-Shop-Agent Backend to Azure Functions..." -ForegroundColor Green

# Check if Azure CLI is logged in
Write-Host "Checking Azure CLI authentication..." -ForegroundColor Yellow
$account = az account show --query "name" -o tsv 2>$null
if (-not $account) {
    Write-Host "❌ Please log in to Azure CLI first: az login" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Logged in as: $account" -ForegroundColor Green

# Check if Function App exists
Write-Host "Checking if Function App exists..." -ForegroundColor Yellow
$functionAppExists = az functionapp show --name $FunctionAppName --resource-group $ResourceGroup --query "name" -o tsv 2>$null
if (-not $functionAppExists) {
    Write-Host "❌ Function App '$FunctionAppName' not found in resource group '$ResourceGroup'" -ForegroundColor Red
    Write-Host "Please run the infrastructure deployment first: ./deploy-minimal.sh" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Function App found: $FunctionAppName" -ForegroundColor Green

# Set Azure Functions to Python 3.11
Write-Host "Configuring Function App runtime..." -ForegroundColor Yellow
az functionapp config set --name $FunctionAppName --resource-group $ResourceGroup --linux-fx-version "Python|3.11" --output none

# Set environment variables from Key Vault
Write-Host "Configuring environment variables..." -ForegroundColor Yellow
$keyVaultName = "igshop-dev-yjhtoi-kv"

# Get secrets from Key Vault
Write-Host "Retrieving secrets from Key Vault..." -ForegroundColor Yellow
$openaiApiKey = az keyvault secret show --vault-name $keyVaultName --name "openai-api-key" --query "value" -o tsv 2>$null
$metaAppId = az keyvault secret show --vault-name $keyVaultName --name "meta-app-id" --query "value" -o tsv 2>$null
$metaAppSecret = az keyvault secret show --vault-name $keyVaultName --name "meta-app-secret" --query "value" -o tsv 2>$null

if ($openaiApiKey -and $metaAppId -and $metaAppSecret) {
    Write-Host "✅ Secrets retrieved from Key Vault" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to retrieve some secrets from Key Vault" -ForegroundColor Red
    Write-Host "Please ensure all secrets are stored in Key Vault" -ForegroundColor Red
    exit 1
}

# Set Function App settings
Write-Host "Setting Function App configuration..." -ForegroundColor Yellow
az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroup --settings `
    "OPENAI_API_KEY=$openaiApiKey" `
    "META_APP_ID=$metaAppId" `
    "META_APP_SECRET=$metaAppSecret" `
    "META_WEBHOOK_VERIFY_TOKEN=ig_shop_webhook_verify_123" `
    "AZURE_KEY_VAULT_URL=https://$keyVaultName.vault.azure.net/" `
    "FUNCTIONS_WORKER_RUNTIME=python" `
    "FUNCTIONS_EXTENSION_VERSION=~4" `
    --output none

# Prepare deployment package
Write-Host "Preparing deployment package..." -ForegroundColor Yellow
$backendPath = "backend"
$tempDeployPath = "deploy-backend-temp"

# Clean up previous deployment
if (Test-Path $tempDeployPath) {
    Remove-Item $tempDeployPath -Recurse -Force
}

# Copy backend files
Copy-Item $backendPath $tempDeployPath -Recurse

# Deploy to Azure Functions
Write-Host "Deploying to Azure Functions..." -ForegroundColor Yellow
Set-Location $tempDeployPath

# Deploy using Azure Functions Core Tools
$deployResult = az functionapp deployment source config-zip --name $FunctionAppName --resource-group $ResourceGroup --src (Get-Location).Path 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed: $deployResult" -ForegroundColor Red
    Set-Location ..
    Remove-Item $tempDeployPath -Recurse -Force
    exit 1
}

# Clean up
Set-Location ..
Remove-Item $tempDeployPath -Recurse -Force

# Test deployment
Write-Host "Testing deployment..." -ForegroundColor Yellow
$functionAppUrl = "https://$FunctionAppName.azurewebsites.net"
Write-Host "Function App URL: $functionAppUrl" -ForegroundColor Cyan

try {
    $healthResponse = Invoke-RestMethod -Uri "$functionAppUrl/health" -Method Get -TimeoutSec 30
    if ($healthResponse.status -eq "healthy") {
        Write-Host "✅ Health check passed!" -ForegroundColor Green
        Write-Host "Backend API is running at: $functionAppUrl" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Health check returned unexpected status: $($healthResponse.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Health check failed, but this might be normal for cold starts" -ForegroundColor Yellow
    Write-Host "Please test manually at: $functionAppUrl/health" -ForegroundColor Yellow
}

Write-Host "🎉 Backend deployment completed!" -ForegroundColor Green
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  Health: $functionAppUrl/health" -ForegroundColor Cyan
Write-Host "  API: $functionAppUrl/api/*" -ForegroundColor Cyan
Write-Host "  Webhook: $functionAppUrl/webhook/instagram" -ForegroundColor Cyan 