# 🔒 Deploy from Private GitHub Repository

This guide shows you how to deploy IG-Shop-Agent when using a **private GitHub repository**.

## 🎯 Why Private Repository?
- ✅ **Secure**: Keep your business logic private
- ✅ **Professional**: Better for commercial projects
- ✅ **Safe**: Protect sensitive configurations
- ✅ **Client-ready**: Suitable for client work

## 🚀 Deployment Methods

### Method 1: Azure Cloud Shell Manual Upload (Easiest)

#### Step 1: Prepare Files Locally
Create a zip file with essential deployment files:
```cmd
# Create a folder with just deployment files
mkdir deploy-package
copy deploy-minimal.sh deploy-package\
copy infra\*.* deploy-package\infra\
xcopy backend deploy-package\backend\ /E /I
```

#### Step 2: Upload to Azure Cloud Shell
1. **Open Azure Cloud Shell**: https://portal.azure.com (click >_ icon)
2. **Choose Bash**
3. **Click Upload** button in Cloud Shell toolbar
4. **Upload your files**:
   - `deploy-minimal.sh`
   - `infra/main.bicep`
   - `infra/parameters.dev.json`
   - Entire `backend/` folder

#### Step 3: Deploy
```bash
# Make script executable
chmod +x deploy-minimal.sh

# Run deployment
./deploy-minimal.sh dev
```

### Method 2: GitHub Clone with Authentication

#### Step 1: Authenticate in Azure Cloud Shell
```bash
# Option A: GitHub CLI (recommended)
gh auth login

# Option B: Generate Personal Access Token
# Go to: https://github.com/settings/tokens
# Create token with 'repo' scope
```

#### Step 2: Clone and Deploy
```bash
# Clone your private repository
git clone https://github.com/yourusername/ig-shop-agent.git
cd ig-shop-agent

# Run deployment
chmod +x deploy-minimal.sh
./deploy-minimal.sh dev
```

### Method 3: Azure DevOps Pipeline (Advanced)

Create a CI/CD pipeline for automated deployment:

#### azure-pipelines.yml
```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: AzureCLI@2
  displayName: 'Deploy IG-Shop-Agent'
  inputs:
    azureSubscription: 'your-service-connection'
    scriptType: 'bash'
    scriptLocation: 'scriptPath'
    scriptPath: './deploy-minimal.sh'
    arguments: 'dev'
```

## 🔐 Security Best Practices with Private Repos

### 1. Environment Variables
Never commit sensitive data. Use Azure Key Vault:
```bash
# Store secrets in Key Vault during deployment
az keyvault secret set --vault-name "your-keyvault" --name "openai-api-key" --value "your-key"
```

### 2. Separate Configuration
Keep sensitive configs in separate files:
```json
// parameters.private.json (never commit)
{
  "openAiApiKey": "your-real-key",
  "metaAppSecret": "your-real-secret"
}
```

### 3. GitHub Secrets
Use GitHub Secrets for CI/CD:
1. Go to: `Settings > Secrets and variables > Actions`
2. Add secrets:
   - `AZURE_CREDENTIALS`
   - `OPENAI_API_KEY`
   - `META_APP_SECRET`

## 📊 Comparison: Private vs Public

| Aspect | Private Repository | Public Repository |
|--------|-------------------|-------------------|
| **Security** | ✅ High | ⚠️ Code visible |
| **Deployment** | Manual steps needed | One-command |
| **Collaboration** | Team only | Open source |
| **Professional** | ✅ Business-ready | Portfolio showcase |
| **Cost** | Same ($28-40/month) | Same ($28-40/month) |

## 🎯 Recommended Approach

**For Business/Commercial Use**: 
- Use **Private Repository**
- Deploy via **Method 1** (manual upload) - simplest
- Store all secrets in **Azure Key Vault**

**For Portfolio/Learning**:
- Use **Public Repository** 
- One-command deployment
- Great for showcasing skills

## 🚀 Expected Results (Same for Both)

After deployment, you'll get:
- **Frontend**: `https://igshop-dev-app.azurestaticapps.net`
- **Backend**: `https://igshop-dev-functions.azurewebsites.net`  
- **API**: Full REST API with all endpoints
- **Cost**: $28-40/month (95% savings)
- **Security**: Azure Key Vault for all secrets

## 🆘 Troubleshooting Private Repos

### Authentication Issues
```bash
# If GitHub authentication fails:
gh auth status
gh auth refresh

# Or use SSH keys:
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add public key to GitHub: Settings > SSH and GPG keys
```

### Upload Issues in Cloud Shell
- **File size limit**: 100MB max per upload
- **Zip large folders**: If backend folder is too big
- **Use git clone**: For large projects

---

**🔒 Bottom Line**: Private repos are perfectly fine and often better for business use. The deployment just requires 1-2 extra steps, but you get the same ultra low-cost platform with better security! 