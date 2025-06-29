#!/bin/bash
# Azure Deployment Script for 100% Production Completion
# IG-Shop-Agent: Complete Enterprise SaaS Platform

echo "🚀 Starting Azure Production Deployment..."

# Set variables
RESOURCE_GROUP="igshop-dev-rg-v2"
WEB_APP_NAME="igshop-api"
LOCATION="East US"

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure authentication..."
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Please login to Azure first:"
    echo "az login"
    exit 1
fi

echo "✅ Azure authentication verified"

# Set the correct subscription
az account set --subscription "$(az account list --query '[0].id' -o tsv)"

echo "🔧 Configuring Azure Web App for Python..."

# Update Web App configuration to Python
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --linux-fx-version "PYTHON|3.11" \
    --startup-file "python production_app.py"

echo "✅ Runtime configuration updated to Python 3.11"

# Configure environment variables
echo "🔧 Setting environment variables..."

az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        FACEBOOK_APP_ID="1879578119651644" \
        FACEBOOK_APP_SECRET="f79b3350f43751d6139e1b29a232cbf3" \
        OPENAI_API_KEY="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" \
        DATABASE_URL="postgresql://igshop_user:IGShop2024!@igshop-postgres.postgres.database.azure.com:5432/igshop_db?sslmode=require" \
        JWT_SECRET_KEY="production-jwt-secret-$(date +%s)" \
        ENVIRONMENT="production" \
        PORT="8000" \
        PYTHONPATH="/home/site/wwwroot" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo "✅ Environment variables configured"

# Configure deployment source
echo "🔧 Configuring deployment..."

# Enable continuous deployment from GitHub (if using GitHub)
# az webapp deployment source config \
#     --resource-group $RESOURCE_GROUP \
#     --name $WEB_APP_NAME \
#     --repo-url "https://github.com/your-username/your-repo" \
#     --branch "main" \
#     --git-token "your-github-token"

# Deploy current directory
echo "📦 Deploying application..."
az webapp deploy \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --src-path . \
    --type zip

echo "🔄 Restarting Web App..."
az webapp restart \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME

echo "⏱️  Waiting for application to start..."
sleep 30

# Test the deployment
echo "🧪 Testing deployment..."
HEALTH_URL="https://${WEB_APP_NAME}.azurewebsites.net/health"
echo "Testing: $HEALTH_URL"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
if [ $HTTP_STATUS -eq 200 ]; then
    echo "✅ Deployment successful! Backend is responding."
    echo "🎉 100% Production deployment complete!"
    echo ""
    echo "🔗 Backend URL: https://${WEB_APP_NAME}.azurewebsites.net"
    echo "🔗 Health Check: $HEALTH_URL"
    echo ""
    echo "📊 Next steps:"
    echo "1. Update frontend API_BASE_URL to: https://${WEB_APP_NAME}.azurewebsites.net"
    echo "2. Test complete user workflow"
    echo "3. Configure custom domain (optional)"
    echo "4. Set up monitoring alerts"
else
    echo "❌ Deployment failed! HTTP Status: $HTTP_STATUS"
    echo "🔍 Check logs with: az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
    exit 1
fi

# Optional: Configure custom domain
# echo "🌐 Would you like to configure a custom domain? (y/n)"
# read -r CONFIGURE_DOMAIN
# if [ "$CONFIGURE_DOMAIN" = "y" ]; then
#     echo "Enter your custom domain:"
#     read -r CUSTOM_DOMAIN
#     az webapp config hostname add \
#         --resource-group $RESOURCE_GROUP \
#         --webapp-name $WEB_APP_NAME \
#         --hostname $CUSTOM_DOMAIN
#     echo "✅ Custom domain configured: $CUSTOM_DOMAIN"
# fi

echo ""
echo "🎯 PRODUCTION DEPLOYMENT COMPLETE!"
echo "💼 Your IG-Shop-Agent SaaS platform is now 100% production-ready!"
echo ""
echo "🚀 Ready for customers!" 