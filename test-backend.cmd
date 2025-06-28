@echo off
echo.
echo ===============================================
echo Testing Both Azure Function Apps
echo ===============================================
echo.

echo Checking Function App configurations...
echo.

echo 1. igshop-dev-functions-v2 (Python):
az functionapp config show --resource-group igshop-dev-rg-v2 --name igshop-dev-functions-v2 --query "{runtime: linuxFxVersion, host: defaultHostName}" --output table

echo.
echo 2. igshop-dev-yjhtoi-api:
az functionapp config show --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --query "{runtime: linuxFxVersion, host: defaultHostName}" --output table

echo.
echo ===============================================
echo Testing Python Function App Endpoints
echo ===============================================
echo.

echo Testing: https://igshop-dev-functions-v2.azurewebsites.net/api/health
curl -s "https://igshop-dev-functions-v2.azurewebsites.net/api/health" || echo [FAILED]

echo.
echo.
echo Testing: https://igshop-dev-functions-v2.azurewebsites.net/api/catalog
curl -s "https://igshop-dev-functions-v2.azurewebsites.net/api/catalog" || echo [FAILED]

echo.
echo.
echo ===============================================
echo Testing Second Function App Endpoints
echo ===============================================
echo.

echo Testing: https://igshop-dev-yjhtoi-api.azurewebsites.net/api/health
curl -s "https://igshop-dev-yjhtoi-api.azurewebsites.net/api/health" || echo [FAILED]

echo.
echo.
echo Done testing both Function Apps!
echo. 