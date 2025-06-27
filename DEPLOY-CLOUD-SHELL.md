# Deploy Using Azure Cloud Shell (Browser-Based)

## Why Use Cloud Shell?
- No local Azure CLI installation needed
- Pre-authenticated with your Azure account
- All tools pre-installed

## Steps:

### 1. Open Azure Cloud Shell
- Go to [portal.azure.com](https://portal.azure.com)
- Click the Cloud Shell icon (>_) in the top toolbar
- Choose "Bash" when prompted

### 2. Upload Project Files
```bash
# Create project directory
mkdir igshop-agent
cd igshop-agent

# Upload the key files (drag & drop in Cloud Shell):
# - deploy-minimal.sh
# - infra/main.bicep  
# - infra/parameters.dev.json
# - backend/ (entire folder)
```

### 3. Set Permissions and Deploy
```bash
# Make deploy script executable
chmod +x deploy-minimal.sh

# Run deployment
./deploy-minimal.sh dev
```

### 4. Alternative: Direct Bicep Deployment
If upload is difficult, here's the direct command:

```bash
# Set variables
RESOURCE_GROUP="igshop-dev-rg"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy infrastructure
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-uri "https://raw.githubusercontent.com/YOUR_REPO/main/infra/main.bicep" \
  --parameters projectName=igshop environment=dev location=eastus \
               postgresAdminUsername=igshop_admin \
               postgresAdminPassword="ChangeMe123!@#" \
               openAiApiKey="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" \
               metaAppId="1879578119651644" \
               metaAppSecret="f79b3350f43751d6139e1b29a232cbf3"
```

## Advantages of Cloud Shell:
- ✅ No installation issues
- ✅ Pre-authenticated
- ✅ Always up-to-date tools
- ✅ Built-in file editor

## After Deployment:
You'll still get the same results:
- **Frontend**: `https://igshop-dev-app.azurestaticapps.net`
- **Backend**: `https://igshop-dev-functions.azurewebsites.net`
- **Cost**: $28-40/month 