# 🚨 CRITICAL BACKEND FIX - Azure Web App Configuration

## **PROBLEM IDENTIFIED**
- Azure Web App configured as Node.js but our backend is Python Flask
- Error: `Cannot find module 'express'` and looking for `server.js`
- Environment variables not properly configured

## **SOLUTION OPTIONS**

### **Option 1: Azure Portal Configuration (RECOMMENDED)**

**Step 1: Fix Runtime**
1. Go to Azure Portal → App Services → igshop-api
2. Navigate to Settings → Configuration → General settings
3. Change "Stack" from Node.js to Python
4. Set "Python version" to 3.11
5. Set "Startup Command" to: `python app_simple.py`

**Step 2: Set Environment Variables**
1. In Configuration → Application settings → Add new settings:

```
DATABASE_URL = postgresql://igshop_admin:IgShop2024!@igshop-postgres.postgres.database.azure.com:5432/igshop_db?sslmode=require
OPENAI_API_KEY = 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
FACEBOOK_APP_ID = 1879578119651644
FACEBOOK_APP_SECRET = f79b3350f43751d6139e1b29a232cbf3
PORT = 8080
WEBSITES_PORT = 8080
SCM_DO_BUILD_DURING_DEPLOYMENT = true
```

**Step 3: Restart App**
- Click "Restart" in the Overview section

### **Option 2: Azure CLI (Alternative)**

Create a batch file with proper syntax:

```cmd
az webapp config set --resource-group igshop-dev-rg-v2 --name igshop-api --linux-fx-version "PYTHON|3.11"
az webapp config appsettings set --resource-group igshop-dev-rg-v2 --name igshop-api --settings PORT=8080
az webapp config appsettings set --resource-group igshop-dev-rg-v2 --name igshop-api --settings WEBSITES_PORT=8080
az webapp config set --resource-group igshop-dev-rg-v2 --name igshop-api --startup-file "python app_simple.py"
az webapp restart --resource-group igshop-dev-rg-v2 --name igshop-api
```

### **Option 3: GitHub Actions Deployment**

The deployment files we created should help Azure automatically detect Python:
- `backend/startup.sh`
- `backend/runtime.txt` 
- `backend/.deployment`

## **VERIFICATION STEPS**

After fixing the configuration:

1. **Check Runtime**: `az webapp config show --name igshop-api --resource-group igshop-dev-rg-v2 --query linuxFxVersion`
2. **Test Health**: Navigate to `https://igshop-api.azurewebsites.net/health`
3. **Test API**: Try `https://igshop-api.azurewebsites.net/api/health`
4. **Check Logs**: Monitor deployment logs for Python installation

## **EXPECTED RESULTS**

✅ **Runtime**: Changed from NODE|20-lts to PYTHON|3.11
✅ **Startup**: Flask app starts with `python app_simple.py`
✅ **Dependencies**: Requirements.txt automatically installed
✅ **API**: All endpoints respond properly
✅ **Frontend**: "Failed to fetch" error resolved

## **FRONTEND CONNECTION**

Once backend is fixed, frontend should connect successfully to:
- Instagram OAuth: `https://igshop-api.azurewebsites.net/auth/instagram`
- Catalog API: `https://igshop-api.azurewebsites.net/api/catalog`
- Orders API: `https://igshop-api.azurewebsites.net/api/orders`

---
**PRIORITY**: CRITICAL - This blocks all frontend functionality
**TIME TO FIX**: 10-15 minutes via Azure Portal 