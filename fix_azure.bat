@echo off
echo 🔧 Fixing Azure Web App Configuration...

echo Setting startup command...
az webapp config set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 production_app:app"

echo Setting environment variables...
az webapp config appsettings set --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api --settings META_APP_ID="1879578119651644" META_APP_SECRET="f79b3350f43751d6139e1b29a232cbf3" OPENAI_API_KEY="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" JWT_SECRET_KEY="production-secret-key-change-in-prod" META_REDIRECT_URI="https://igshop-dev-yjhtoi-api.azurewebsites.net/auth/instagram/callback" SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo Restarting app...
az webapp restart --resource-group igshop-dev-rg-v2 --name igshop-dev-yjhtoi-api

echo ✅ Configuration updated! Testing in 30 seconds...
timeout /t 30 /nobreak

echo Testing backend...
python verify_backend.py

echo.
echo 🌐 Frontend URL: https://red-island-0b863450f.2.azurestaticapps.net
echo 🔗 Backend URL: https://igshop-dev-yjhtoi-api.azurewebsites.net
pause 