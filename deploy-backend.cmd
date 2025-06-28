@echo off
echo ========================================
echo    IG Shop Agent - Backend Deployment
echo ========================================
echo.

echo [1/3] Deploying Azure Infrastructure...
az deployment group create ^
  --resource-group "igshop-dev-rg-v2" ^
  --template-file "infra/main.bicep" ^
  --parameters "infra/parameters.deployment.json" ^
  --name "igshop-backend-deployment"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Infrastructure deployment failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Getting deployment outputs...
az deployment group show ^
  --resource-group "igshop-dev-rg-v2" ^
  --name "igshop-backend-deployment" ^
  --query "properties.outputs" ^
  --output table

echo.
echo [3/3] Deployment completed successfully!
echo.
echo Next steps:
echo 1. Deploy backend code to Azure Functions
echo 2. Configure Instagram webhooks
echo 3. Test the complete system
echo.
pause 