#!/bin/bash

# IG-Shop-Agent Ultra Low-Cost One-Click Deployment Script
# This script deploys the entire platform for under $30/month (excluding OpenAI usage)

set -e

echo "🚀 IG-Shop-Agent Ultra Low-Cost Deployment"
echo "=========================================="
echo "Target Cost: $28-40/month (excluding OpenAI usage)"
echo "Savings: $250+ per month compared to full enterprise setup"
echo ""

# Configuration
ENVIRONMENT=${1:-dev}
RESOURCE_GROUP="igshop-${ENVIRONMENT}-rg"
LOCATION="eastus"
SUBSCRIPTION_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI not found. Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Initiating login..."
    az login
fi

# Get subscription info
SUBSCRIPTION_INFO=$(az account show --output json)
SUBSCRIPTION_ID=$(echo $SUBSCRIPTION_INFO | jq -r '.id')
SUBSCRIPTION_NAME=$(echo $SUBSCRIPTION_INFO | jq -r '.name')

print_success "Using subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"

# Prompt for OpenAI API key if not set
if ! grep -q "your-openai-api-key-here" infra/parameters.${ENVIRONMENT}.json; then
    print_success "OpenAI API key already configured"
else
    print_warning "OpenAI API key needs to be configured"
    echo "You need an OpenAI API key for the AI agent functionality."
    echo "Get one from: https://platform.openai.com/api-keys"
    read -p "Enter your OpenAI API key: " OPENAI_KEY
    
    # Update parameters file
    sed -i "s/your-openai-api-key-here/$OPENAI_KEY/g" infra/parameters.${ENVIRONMENT}.json
    print_success "OpenAI API key configured"
fi

# Create resource group
print_step "Creating resource group: $RESOURCE_GROUP"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output table

print_success "Resource group created"

# Deploy infrastructure
print_step "Deploying ultra low-cost infrastructure..."
echo "This includes:"
echo "  - PostgreSQL Container (pgvector) - ~$15/month"
echo "  - Azure Functions (Consumption) - ~$2-5/month"
echo "  - Storage Account - ~$1-3/month"
echo "  - Static Web App - ~$9/month"
echo "  - Other services - ~$1-5/month"

DEPLOYMENT_NAME="igshop-ultralow-$(date +%Y%m%d-%H%M%S)"

cd infra
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters @parameters.${ENVIRONMENT}.json \
    --name "$DEPLOYMENT_NAME" \
    --output table

print_success "Infrastructure deployment completed!"

# Get deployment outputs
print_step "Retrieving deployment information..."
OUTPUTS=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$DEPLOYMENT_NAME" \
    --query properties.outputs \
    --output json)

# Extract important values
FUNCTION_APP_NAME=$(echo $OUTPUTS | jq -r '.functionAppName.value')
FUNCTION_APP_URL=$(echo $OUTPUTS | jq -r '.functionAppUrl.value')
STATIC_WEB_APP_NAME=$(echo $OUTPUTS | jq -r '.staticWebAppName.value')
STATIC_WEB_APP_URL=$(echo $OUTPUTS | jq -r '.staticWebAppUrl.value')
POSTGRES_FQDN=$(echo $OUTPUTS | jq -r '.postgresContainerFQDN.value')
KEY_VAULT_NAME=$(echo $OUTPUTS | jq -r '.keyVaultName.value')
DNS_ZONE_NAME=$(echo $OUTPUTS | jq -r '.dnsZoneName.value')

# Save deployment info
cat > deployment-info.json << EOF
{
  "environment": "$ENVIRONMENT",
  "resourceGroup": "$RESOURCE_GROUP",
  "functionAppName": "$FUNCTION_APP_NAME",
  "functionAppUrl": "$FUNCTION_APP_URL",
  "staticWebAppName": "$STATIC_WEB_APP_NAME",
  "staticWebAppUrl": "$STATIC_WEB_APP_URL",
  "postgresFQDN": "$POSTGRES_FQDN",
  "keyVaultName": "$KEY_VAULT_NAME",
  "dnsZoneName": "$DNS_ZONE_NAME",
  "deploymentDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "Deployment information saved to deployment-info.json"

cd ..

# Deploy backend code
print_step "Deploying backend code to Azure Functions..."

# Check if Azure Functions Core Tools is installed
if ! command -v func &> /dev/null; then
    print_warning "Azure Functions Core Tools not found"
    echo "Installing Azure Functions Core Tools..."
    npm install -g azure-functions-core-tools@4 --unsafe-perm true
fi

# Create requirements.txt for Functions
cat > backend/requirements.txt << EOF
azure-functions
azure-functions-worker
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
psycopg2-binary
openai
azure-openai
azure-identity
azure-keyvault-secrets
azure-storage-blob
azure-servicebus
httpx
python-jose[cryptography]
python-multipart
pydantic
pydantic-settings
structlog
EOF

# Create host.json for Functions
cat > backend/host.json << EOF
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "functionTimeout": "00:05:00"
}
EOF

# Deploy functions
cd backend
func azure functionapp publish $FUNCTION_APP_NAME --python

print_success "Backend deployed to Azure Functions"

cd ..

# Deploy frontend
print_step "Setting up frontend deployment..."

# Check if the frontend is already deployed
if [[ "$STATIC_WEB_APP_URL" != "null" ]]; then
    print_success "Frontend deployed at: $STATIC_WEB_APP_URL"
    print_warning "To connect your GitHub repository:"
    echo "1. Go to: https://portal.azure.com"
    echo "2. Navigate to your Static Web App: $STATIC_WEB_APP_NAME"
    echo "3. Click 'Manage deployment token'"
    echo "4. Add the deployment token to your GitHub repository secrets"
    echo "5. The frontend will auto-deploy on git push"
fi

# Initialize database
print_step "Initializing database with pgvector..."

# Create init script
cat > init-db.sql << EOF
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database schema (tables will be created by the application)
-- This script can be run manually or via the application

SELECT 'Database initialized successfully' as status;
EOF

print_success "Database initialization script created: init-db.sql"

# Cost summary
print_step "Deployment Summary"
echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "====================================="
echo ""
echo "📊 ULTRA LOW-COST ARCHITECTURE DEPLOYED:"
echo "├── PostgreSQL Container (pgvector): ~\$15/month"
echo "├── Azure Functions (Consumption): ~\$2-5/month"  
echo "├── Storage Account: ~\$1-3/month"
echo "├── Static Web App: ~\$9/month"
echo "├── Key Vault & Other: ~\$1-5/month"
echo "└── Total: ~\$28-40/month (excluding OpenAI usage)"
echo ""
echo "💰 COST SAVINGS: \$250+/month vs enterprise setup"
echo ""
echo "🔗 ACCESS POINTS:"
echo "├── API Backend: $FUNCTION_APP_URL"
echo "├── Frontend: $STATIC_WEB_APP_URL"
echo "├── Database: $POSTGRES_FQDN:5432"
echo "└── Domain: $DNS_ZONE_NAME (configure DNS)"
echo ""
echo "🔧 NEXT STEPS:"
echo "1. Configure Instagram/Meta API credentials in Key Vault"
echo "2. Connect GitHub repository for auto-deployment"
echo "3. Set up custom domain (optional)"
echo "4. Test the API endpoints"
echo "5. Configure Instagram webhook URL"
echo ""
echo "📚 DOCUMENTATION:"
echo "- API Docs: $FUNCTION_APP_URL/docs"
echo "- Health Check: $FUNCTION_APP_URL/health"
echo "- Admin Guide: docs/IG_Shop_Agent_Technical_Analysis.md"
echo ""
echo "🚀 YOUR IG-SHOP-AGENT IS READY!"

# Create quick test script
cat > test-deployment.sh << EOF
#!/bin/bash
echo "Testing IG-Shop-Agent deployment..."
echo "API Health Check:"
curl -s "$FUNCTION_APP_URL/health" | jq .
echo ""
echo "Frontend Check:"
curl -s -I "$STATIC_WEB_APP_URL" | head -n 1
EOF

chmod +x test-deployment.sh

print_success "Quick test script created: ./test-deployment.sh"
print_success "Deployment completed! Total cost: ~\$30/month 💰"

echo ""
echo "Run './test-deployment.sh' to verify your deployment" 