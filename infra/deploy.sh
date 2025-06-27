#!/bin/bash

# IG-Shop-Agent Infrastructure Deployment Script
# Usage: ./deploy.sh [environment] [resource-group-name] [subscription-id]

set -e

# Default values
ENVIRONMENT=${1:-dev}
RESOURCE_GROUP=${2:-igshop-${ENVIRONMENT}-rg}
SUBSCRIPTION_ID=${3}
LOCATION="eastus"

echo "🚀 Starting IG-Shop-Agent infrastructure deployment..."
echo "Environment: $ENVIRONMENT"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"

# Check if Azure CLI is logged in
if ! az account show &> /dev/null; then
    echo "❌ Please log in to Azure CLI first: az login"
    exit 1
fi

# Set subscription if provided
if [ ! -z "$SUBSCRIPTION_ID" ]; then
    echo "📋 Setting subscription to: $SUBSCRIPTION_ID"
    az account set --subscription "$SUBSCRIPTION_ID"
fi

# Create resource group if it doesn't exist
echo "📦 Creating resource group: $RESOURCE_GROUP"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output table

# Deploy the Bicep template
echo "🏗️ Deploying infrastructure..."
DEPLOYMENT_NAME="igshop-infra-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters @parameters.${ENVIRONMENT}.json \
    --name "$DEPLOYMENT_NAME" \
    --output table

# Get deployment outputs
echo "📤 Getting deployment outputs..."
OUTPUTS=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DEPLOYMENT_NAME" \
    --query properties.outputs \
    --output json)

# Display important connection information
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Important Resources Created:"
echo "================================"
echo "Storage Account: $(echo $OUTPUTS | jq -r '.storageAccountName.value')"
echo "Key Vault: $(echo $OUTPUTS | jq -r '.keyVaultName.value')"
echo "PostgreSQL Server: $(echo $OUTPUTS | jq -r '.postgresServerName.value')"
echo "Service Bus: $(echo $OUTPUTS | jq -r '.serviceBusNamespace.value')"
echo "AI Search: $(echo $OUTPUTS | jq -r '.searchServiceName.value')"
echo "OpenAI Service: $(echo $OUTPUTS | jq -r '.openAiServiceName.value')"
echo "Backend App Service: $(echo $OUTPUTS | jq -r '.backendAppServiceName.value')"
echo "Function App: $(echo $OUTPUTS | jq -r '.functionAppName.value')"
echo "Static Web App: $(echo $OUTPUTS | jq -r '.staticWebAppName.value')"
echo "Application Insights: $(echo $OUTPUTS | jq -r '.applicationInsightsName.value')"
echo ""

# Save outputs to file for CI/CD
echo "$OUTPUTS" > deployment-outputs.json
echo "💾 Deployment outputs saved to: deployment-outputs.json"

echo ""
echo "🔧 Next Steps:"
echo "1. Update your GitHub repository URL in the Static Web App"
echo "2. Configure environment variables for your applications"
echo "3. Set up CI/CD pipeline using the outputs above"
echo "4. Initialize the PostgreSQL database with the schema"
echo ""
echo "🎉 Infrastructure deployment complete!"
