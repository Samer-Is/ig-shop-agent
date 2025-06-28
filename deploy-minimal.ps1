# IG-Shop-Agent Ultra Low-Cost Deployment Script (PowerShell)
param(
    [Parameter(Mandatory = $true)]
    [string]$Environment
)

Write-Host "🚀 IG-Shop-Agent Ultra Low-Cost Deployment" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Expected Cost: $28-40/month (vs $800+/month original)" -ForegroundColor Yellow

# Configuration
$PROJECT_NAME = "igshop"
$LOCATION = "eastus"
$RESOURCE_GROUP = "$PROJECT_NAME-$Environment-rg"

Write-Host "`n🔍 Checking Azure CLI authentication..." -ForegroundColor Blue
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✅ Authenticated as: $($account.user.name)" -ForegroundColor Green
    Write-Host "✅ Subscription: $($account.name)" -ForegroundColor Green
    Write-Host "✅ Tenant: $($account.tenantId)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Not authenticated. Please run: az login --use-device-code" -ForegroundColor Red
    exit 1
}

Write-Host "`n📦 Creating resource group..." -ForegroundColor Blue
az group create --name $RESOURCE_GROUP --location $LOCATION --output table

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create resource group" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Resource group created: $RESOURCE_GROUP" -ForegroundColor Green

Write-Host "`n🏗️ Deploying infrastructure (this may take 5-10 minutes)..." -ForegroundColor Blue
Write-Host "📊 Deploying ultra low-cost architecture:" -ForegroundColor Cyan
Write-Host "   • PostgreSQL Container: ~$15/month (vs $100 Azure DB)" -ForegroundColor White
Write-Host "   • Azure Functions: ~$3/month (vs $150 App Service)" -ForegroundColor White
Write-Host "   • Vector Search (pgvector): FREE (vs $250 AI Search)" -ForegroundColor White
Write-Host "   • Static Web App: ~$9/month" -ForegroundColor White
Write-Host "   • Storage + Others: ~$5/month" -ForegroundColor White

$deploymentResult = az deployment group create `
    --resource-group $RESOURCE_GROUP `
    --template-file "infra/main.bicep" `
    --parameters "infra/parameters.$Environment.json" `
    --output json

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Infrastructure deployment failed" -ForegroundColor Red
    Write-Host "📋 Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "   • Check if all required parameters are set in infra/parameters.$Environment.json" -ForegroundColor White
    Write-Host "   • Verify you have sufficient permissions in the subscription" -ForegroundColor White
    Write-Host "   • Check Azure portal for detailed error messages" -ForegroundColor White
    exit 1
}

$deployment = $deploymentResult | ConvertFrom-Json
Write-Host "✅ Infrastructure deployed successfully!" -ForegroundColor Green

# Extract deployment outputs
$outputs = $deployment.properties.outputs
$functionAppName = $outputs.functionAppName.value
$staticWebAppName = $outputs.staticWebAppName.value
$functionAppUrl = $outputs.functionAppUrl.value
$staticWebAppUrl = $outputs.staticWebAppUrl.value

Write-Host "`n📱 Deploying backend application..." -ForegroundColor Blue
Write-Host "📦 Creating deployment package..." -ForegroundColor Cyan

# Create a zip file of the backend
$backendPath = "backend"
$zipPath = "backend-deployment.zip"

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

# Create zip file using PowerShell
Compress-Archive -Path "$backendPath\*" -DestinationPath $zipPath -Force
Write-Host "✅ Backend package created: $zipPath" -ForegroundColor Green

Write-Host "🚀 Deploying to Azure Functions..." -ForegroundColor Blue
az functionapp deployment source config-zip `
    --resource-group $RESOURCE_GROUP `
    --name $functionAppName `
    --src $zipPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green

Write-Host "`n🌐 Deploying frontend application..." -ForegroundColor Blue
Write-Host "📦 Building frontend..." -ForegroundColor Cyan

# Navigate to frontend directory and build
Push-Location "ig-shop-agent-dashboard"
try {
    # Install dependencies and build
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ npm install failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ npm build failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "✅ Frontend built successfully!" -ForegroundColor Green
}
finally {
    Pop-Location
}

# Deploy frontend to Static Web App
Write-Host "🚀 Deploying to Static Web App..." -ForegroundColor Blue
az staticwebapp environment set `
    --name $staticWebAppName `
    --resource-group $RESOURCE_GROUP `
    --source "ig-shop-agent-dashboard/dist"

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Static Web App deployment may need manual setup" -ForegroundColor Yellow
    Write-Host "📋 You can manually upload the 'ig-shop-agent-dashboard/dist' folder to your Static Web App" -ForegroundColor White
}

# Clean up
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

Write-Host "`n🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

Write-Host "`n📋 Your IG-Shop-Agent Platform URLs:" -ForegroundColor Cyan
Write-Host "🌐 Frontend Dashboard: $staticWebAppUrl" -ForegroundColor Yellow
Write-Host "⚡ Backend API: $functionAppUrl" -ForegroundColor Yellow
Write-Host "🪝 Instagram Webhook: $functionAppUrl/api/webhook/instagram" -ForegroundColor Yellow

Write-Host "`n💰 Cost Breakdown (Monthly):" -ForegroundColor Cyan
Write-Host "   • PostgreSQL Container: ~$15-20" -ForegroundColor Green
Write-Host "   • Azure Functions: ~$2-5" -ForegroundColor Green
Write-Host "   • Storage Account: ~$1-3" -ForegroundColor Green
Write-Host "   • Static Web App: ~$9" -ForegroundColor Green
Write-Host "   • Other services: ~$1-3" -ForegroundColor Green
Write-Host "   📊 TOTAL: $28-40/month (95% savings!)" -ForegroundColor Yellow

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. 🔗 Configure Instagram webhook in Meta Developer Console:" -ForegroundColor White
Write-Host "   Webhook URL: $functionAppUrl/api/webhook/instagram" -ForegroundColor Yellow
Write-Host "`n2. 🏪 Access your dashboard at: $staticWebAppUrl" -ForegroundColor White
Write-Host "`n3. 🤖 Test the AI agent by sending a DM to your Instagram business account" -ForegroundColor White

Write-Host "`n🎯 Your ultra low-cost Instagram automation platform is now LIVE!" -ForegroundColor Green
Write-Host "🚀 Enjoy your 95% cost savings and Arabic-powered AI agent!" -ForegroundColor Yellow 