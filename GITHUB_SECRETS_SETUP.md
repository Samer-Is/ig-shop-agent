# 🔐 GitHub Secrets Setup for Automated Deployment

## 🎯 REQUIRED: Add Azure Publish Profile to GitHub

### Step 1: Get Azure Publish Profile
Run this command (or check output above):
```bash
az webapp deployment list-publishing-profiles --name igshop-dev-yjhtoi-api --resource-group igshop-dev-rg-v2 --xml
```

### Step 2: Add to GitHub Secrets
1. Go to your GitHub repository: `https://github.com/Samer-Is/ig-shop-agent`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
5. Value: Copy the entire XML output from Step 1
6. Click **Add secret**

### Step 3: Trigger Deployment (if needed)
If the workflow failed due to missing secrets:
1. Go to **Actions** tab in GitHub
2. Click **Re-run jobs** on the failed workflow

## 🎉 AFTER SETUP:

### Your deployment will be 100% automated:
- ✅ Push to main branch → Auto-deploy to Azure
- ✅ Flask backend deployed to `igshop-dev-yjhtoi-api.azurewebsites.net`
- ✅ Environment variables set automatically
- ✅ Health checks performed

### Test URLs after deployment:
- **Health**: `https://igshop-dev-yjhtoi-api.azurewebsites.net/health`
- **Frontend**: `https://red-island-0b863450f.2.azurestaticapps.net`

## 🚀 DEPLOYMENT STATUS:
**Backend**: Automated via GitHub Actions
**Frontend**: Already live on Azure Static Web Apps
**Database**: PostgreSQL ready on Azure
**Integration**: Complete end-to-end system 