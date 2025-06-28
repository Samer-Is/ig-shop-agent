@echo off
echo.
echo ===============================================
echo Deploying Clean Python Function App
echo ===============================================
echo.

cd backend

echo Creating clean deployment package...
if exist ..\backend-clean-final.zip del ..\backend-clean-final.zip
PowerShell -Command "Compress-Archive -Path function_app.py,host.json,requirements.txt,.funcignore -DestinationPath ../backend-clean-final.zip -Force"

echo.
echo Deploying to Azure with build-remote...
az functionapp deployment source config-zip ^
  --resource-group igshop-dev-rg-v2 ^
  --name igshop-dev-functions-v2 ^
  --src ../backend-clean-final.zip ^
  --build-remote true

echo.
echo Waiting for deployment to complete...
timeout /t 30 /nobreak

echo.
echo Testing deployment...
curl -s "https://igshop-dev-functions-v2.azurewebsites.net/api/health"

echo.
echo ===============================================
echo Deployment completed!
echo =============================================== 