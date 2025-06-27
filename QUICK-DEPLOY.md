# IG-Shop-Agent Ultra Low-Cost Deployment Guide

## Your Azure Details ✅
- **Subscription**: Azure subscription 1
- **Directory**: Default Directory (SamerHishamoutlook.onmicrosoft.com)
- **Region**: East US
- **Expected Cost**: $28-40/month (vs $800+/month original)

## Quick Deploy (3 Minutes)

### Step 1: Restart PowerShell
**IMPORTANT**: Close this PowerShell window and open a new one for Azure CLI to work.

### Step 2: Navigate to Project
```powershell
cd "C:\Users\samer.ismail\Desktop\minmax_agent"
```

### Step 3: Login to Azure
```powershell
az login
```
- This will open your browser
- Login with your Azure account
- Select "Azure subscription 1" if prompted

### Step 4: Deploy Everything
```powershell
./deploy-minimal.sh dev
```

## What Gets Deployed

### Infrastructure ($28-40/month)
- ✅ PostgreSQL Container with pgvector: $15-20/month
- ✅ Azure Functions (Consumption): $2-5/month  
- ✅ Storage Account: $1-3/month
- ✅ Static Web App: $9/month
- ✅ Key Vault for secrets: $1/month
- ✅ DNS Zone for custom domains: $1/month

### Applications
- ✅ FastAPI Backend with all routes
- ✅ AI Agent with Jordanian Arabic support
- ✅ Vector search with pgvector (FREE vs $250/month)
- ✅ Multi-tenant architecture
- ✅ Instagram webhook handling
- ✅ Complete dashboard

## After Deployment

### URLs You'll Get
- **Frontend**: `https://igshop-dev-app.azurestaticapps.net`
- **Backend API**: `https://igshop-dev-functions.azurewebsites.net`
- **Webhook**: `https://igshop-dev-functions.azurewebsites.net/api/webhook/instagram`

### Next Steps
1. **Configure Instagram**: Use the webhook URL in your Meta app
2. **Test the system**: Create a business profile and start chatting
3. **Add custom domain**: Use the DNS zone for your own domain

## Cost Savings Summary
- **Before**: $800-1200/month
- **After**: $28-40/month  
- **Savings**: $760-1160/month (95% reduction!)

## Support
If anything fails during deployment, the script will show clear error messages and suggestions.

---
**Ready to deploy? Just restart PowerShell and follow the 4 steps above!** 