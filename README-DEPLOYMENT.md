# IG-Shop-Agent Ultra Low-Cost Deployment Guide

**🎯 Target: Complete Instagram DM automation platform for under $30/month**

## 🏗️ Architecture Overview (Ultra Low-Cost)

### **Cost Breakdown**
| Service | Monthly Cost | Description |
|---------|-------------|-------------|
| PostgreSQL Container (pgvector) | $15-20 | 1 CPU, 2GB RAM Container Instance |
| Azure Functions (Consumption) | $2-5 | Pay per execution (1M free) |
| Storage Account | $1-3 | Free tier + minimal usage |
| Static Web App | $9 | Standard tier for frontend |
| Key Vault & Other | $1-5 | Basic services |
| **Total** | **$28-40/month** | **Excluding OpenAI usage** |
| **Savings** | **$250+/month** | **vs Enterprise setup** |

### **What You Get**
- ✅ Complete Instagram DM automation
- ✅ AI agent with Jordanian Arabic support
- ✅ Multi-tenant SaaS platform
- ✅ Vector search with pgvector
- ✅ Real-time message processing
- ✅ Professional dashboard
- ✅ Custom domain support
- ✅ Auto-scaling infrastructure

## 🚀 One-Click Deployment

### **Prerequisites**
1. **Azure Account** (free tier works)
2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
3. **Azure CLI** ([Install here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))

### **Deploy in 3 Commands**

```bash
# 1. Clone and navigate
git clone <your-repo>
cd minmax_agent

# 2. Run one-click deployment
./deploy-minimal.sh dev

# 3. Test deployment
./test-deployment.sh
```

That's it! Your entire platform will be live in ~15 minutes.

## 📋 Step-by-Step Manual Deployment

### **Step 1: Prepare Environment**

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "Your Subscription Name"

# Update OpenAI API key in parameters
# Edit infra/parameters.dev.json and replace "your-openai-api-key-here"
```

### **Step 2: Deploy Infrastructure**

```bash
cd infra

# Create resource group
az group create --name igshop-dev-rg --location eastus

# Deploy infrastructure
az deployment group create \
    --resource-group igshop-dev-rg \
    --template-file main.bicep \
    --parameters @parameters.dev.json \
    --name igshop-deployment
```

### **Step 3: Deploy Backend**

```bash
cd ../backend

# Install Azure Functions Core Tools (if not installed)
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Deploy functions
func azure functionapp publish <your-function-app-name> --python
```

### **Step 4: Setup Frontend**

The frontend is automatically configured but needs GitHub connection:

1. Go to Azure Portal → Static Web Apps
2. Find your app: `igshop-dev-xxxxx-swa`
3. Click "Manage deployment token"
4. Add token to GitHub repository secrets
5. Push to trigger deployment

### **Step 5: Initialize Database**

```bash
# Connect to PostgreSQL container
psql postgresql://igshop_admin:password@<container-fqdn>:5432/igshop_dev_db

# Run initialization
CREATE EXTENSION IF NOT EXISTS vector;
```

## 🔧 Configuration

### **Environment Variables**

The deployment automatically configures these in Azure Key Vault:

- `DATABASE_URL` - PostgreSQL connection string
- `AZURE_OPENAI_ENDPOINT` - OpenAI service endpoint
- `AZURE_OPENAI_API_KEY` - OpenAI API key
- `AZURE_STORAGE_CONNECTION_STRING` - Storage connection
- `SERVICE_BUS_CONNECTION_STRING` - Service Bus connection

### **Instagram/Meta API Setup**

1. **Create Meta Developer Account**
   - Go to [developers.facebook.com](https://developers.facebook.com)
   - Create new app
   - Add Instagram Basic Display product

2. **Configure Webhook**
   - Webhook URL: `https://your-function-app.azurewebsites.net/api/webhook/instagram`
   - Verify token: Set in Key Vault as `META_WEBHOOK_VERIFY_TOKEN`

3. **Get Tokens**
   - Add `META_ACCESS_TOKEN` to Key Vault
   - Add `META_PAGE_ID` to Key Vault

## 🌐 Custom Domain Setup

### **Option 1: Azure DNS Zone (Included)**

```bash
# The deployment creates: igshop-dev-xxxxx.com
# Configure DNS records:
# A Record: @ → Static Web App IP
# CNAME: api → Function App URL
```

### **Option 2: External Domain**

```bash
# Point your domain to:
# Frontend: your-static-web-app.azurestaticapps.net
# API: your-function-app.azurewebsites.net
```

## 🧪 Testing

### **Health Check**
```bash
curl https://your-function-app.azurewebsites.net/api/health
```

### **API Test**
```bash
# Register user
curl -X POST https://your-function-app.azurewebsites.net/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","instagram_handle":"testshop","display_name":"Test Shop"}'

# Chat with AI
curl -X POST https://your-function-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message":"مرحبا","sender":"test_user"}'
```

## 📊 Monitoring & Analytics

### **Azure Application Insights**
- Automatic logging and monitoring
- Performance metrics
- Error tracking
- Custom dashboards

### **Cost Monitoring**
```bash
# Check monthly costs
az consumption usage list --output table

# Set budget alerts
az consumption budget create \
  --budget-name "igshop-budget" \
  --amount 50 \
  --time-grain Monthly
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Functions not starting**
   ```bash
   # Check logs
   func azure functionapp logstream <function-app-name>
   ```

2. **Database connection issues**
   ```bash
   # Verify container is running
   az container show --resource-group igshop-dev-rg --name igshop-dev-xxxxx-postgres
   ```

3. **OpenAI API errors**
   ```bash
   # Check API key in Key Vault
   az keyvault secret show --vault-name igshop-dev-xxxxx-kv --name openai-api-key
   ```

## 📈 Scaling

### **When to Scale Up**

| Metric | Threshold | Action |
|--------|-----------|--------|
| Users | >100 tenants | Upgrade PostgreSQL to 4GB RAM |
| Messages | >10K/day | Add more Function instances |
| Storage | >100GB | Upgrade storage tier |
| Monthly Cost | >$100 | Consider enterprise architecture |

### **Scaling Commands**

```bash
# Scale PostgreSQL container
az container update \
  --resource-group igshop-dev-rg \
  --name igshop-dev-xxxxx-postgres \
  --memory 4

# Scale Functions (automatic with consumption plan)
# No action needed - auto-scales

# Scale storage
az storage account update \
  --name igshopstorage \
  --sku Standard_GRS
```

## 🚨 Security

### **Production Checklist**

- [ ] Change default passwords
- [ ] Enable Azure AD authentication
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS certificates
- [ ] Set up backup policies
- [ ] Configure monitoring alerts
- [ ] Review access policies
- [ ] Enable audit logging

### **Security Commands**

```bash
# Enable firewall
az postgres flexible-server firewall-rule create \
  --resource-group igshop-dev-rg \
  --name igshop-dev-xxxxx-pg \
  --rule-name "AllowAzureServices" \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Configure SSL
az functionapp config set \
  --resource-group igshop-dev-rg \
  --name igshop-dev-xxxxx-api \
  --ftps-state Disabled
```

## 📞 Support

### **Getting Help**

1. **Documentation**: Check `docs/IG_Shop_Agent_Technical_Analysis.md`
2. **Logs**: Use Application Insights for debugging
3. **Community**: GitHub Issues for community support
4. **Azure Support**: Azure support tickets for infrastructure issues

### **Contact**

- **Technical Issues**: Create GitHub issue
- **Azure Billing**: Azure support portal
- **OpenAI Issues**: OpenAI support

## 🎉 Success!

Your IG-Shop-Agent is now live for under $30/month! 

**Next Steps:**
1. Configure your Instagram business account
2. Add your product catalog
3. Customize AI agent responses
4. Invite your team members
5. Start processing customer messages

**Happy selling! 🛍️** 