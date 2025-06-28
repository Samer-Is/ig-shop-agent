@echo off
echo.
echo ===============================================
echo Fixing Azure Function App Runtime Configuration
echo ===============================================
echo.

echo Setting Python runtime...
az functionapp config appsettings set ^
  --resource-group igshop-dev-rg-v2 ^
  --name igshop-dev-functions-v2 ^
  --settings "FUNCTIONS_WORKER_RUNTIME=python"

echo.
echo Setting Functions version...
az functionapp config appsettings set ^
  --resource-group igshop-dev-rg-v2 ^
  --name igshop-dev-functions-v2 ^
  --settings "FUNCTIONS_EXTENSION_VERSION=~4"

echo.
echo Setting worker indexing...
az functionapp config appsettings set ^
  --resource-group igshop-dev-rg-v2 ^
  --name igshop-dev-functions-v2 ^
  --settings "AzureWebJobsFeatureFlags=EnableWorkerIndexing"

echo.
echo Restarting Function App...
az functionapp restart ^
  --resource-group igshop-dev-rg-v2 ^
  --name igshop-dev-functions-v2

echo.
echo ===============================================
echo Runtime configuration completed!
echo =============================================== 