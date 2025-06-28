@echo off
echo ========================================
echo    IG Shop Agent - Phase 1 Deployment
echo    (Core Infrastructure Only)
echo ========================================
echo.

echo [1/2] Deploying Core Infrastructure...
echo - Storage Account
echo - Key Vault  
echo - Function App
echo - Application Insights
echo.

az deployment group create ^
  --resource-group "igshop-dev-rg-v2" ^
  --template-file "infra/main-phase1.bicep" ^
  --parameters "infra/parameters.phase1.json" ^
  --name "igshop-phase1-deployment"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Phase 1 deployment failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Getting deployment outputs...
az deployment group show ^
  --resource-group "igshop-dev-rg-v2" ^
  --name "igshop-phase1-deployment" ^
  --query "properties.outputs" ^
  --output table

echo.
echo ========================================
echo    PHASE 1 COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo ✅ Function App ready for backend code
echo ✅ Storage and Key Vault configured  
echo ✅ All secrets stored securely
echo.
echo NEXT STEPS:
echo 1. Deploy backend code to Function App
echo 2. Add PostgreSQL database (Phase 2)
echo 3. Configure Instagram webhooks
echo 4. Test the system end-to-end
echo.
pause 