# 🔐 GitHub Secrets Setup for Automated Deployment

## 🚨 URGENT: Add These Secrets to GitHub Repository

You need to add these secrets to your GitHub repository to enable automated deployment.

### Step 1: Get Azure Service Principal Credentials

Run this command to create a service principal and get the credentials:

```bash
az ad sp create-for-rbac --name "igshop-github-actions" \
  --role contributor \
  --scopes /subscriptions/722afad3-883c-4fdc-af24-8cf1f828f780/resourceGroups/igshop-dev-rg-v2 \
  --sdk-auth
```

Copy the JSON output and use it for the `AZURE_CREDENTIALS` secret.

### Step 2: Get Azure Web App Publish Profile

Run this command to get the publish profile:

```bash
az webapp deployment list-publishing-profiles \
  --name igshop-dev-yjhtoi-api \
  --resource-group igshop-dev-rg-v2 \
  --xml
```

Copy the XML output and use it for the `AZURE_WEBAPP_PUBLISH_PROFILE` secret.

### Step 3: Add Secrets to GitHub

1. Go to your GitHub repository: https://github.com/Samer-Is/ig-shop-agent
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of these:

#### AZURE_CREDENTIALS
```json
{
  "clientId": "YOUR_CLIENT_ID_FROM_STEP_1",
  "clientSecret": "YOUR_CLIENT_SECRET_FROM_STEP_1", 
  "subscriptionId": "722afad3-883c-4fdc-af24-8cf1f828f780",
  "tenantId": "062f77f6-a70b-44c6-ae4a-b709e3cfd2ed",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

#### AZURE_WEBAPP_PUBLISH_PROFILE
Paste the complete XML output from Step 2.

#### AZURE_STATIC_WEB_APPS_API_TOKEN
```
4a85238cfe7fc881ece2b2cb5f789d88c9e32ecd5ef192ad170226df4c3fedf502-98cddeba-6028-4b64-b5bb-50c971d5c31700f201506c98c40f
```

### Step 4: Trigger Deployment

After adding the secrets:

1. Go to GitHub Actions: https://github.com/Samer-Is/ig-shop-agent/actions
2. Click **Deploy Backend Application**
3. Click **Run workflow**
4. Select branch: `production-deployment`
5. Click **Run workflow**

### Step 5: Monitor Deployment

Watch the workflow execution at:
https://github.com/Samer-Is/ig-shop-agent/actions

### Step 6: Test Deployment

After deployment completes, test these URLs:

- **Backend Health**: https://igshop-dev-yjhtoi-api.azurewebsites.net/health
- **Backend Root**: https://igshop-dev-yjhtoi-api.azurewebsites.net/
- **Frontend**: https://igshop-dev-yjhtoi-swa.azurestaticapps.net

## 🔧 Azure Resources Status

✅ **Web App**: `igshop-dev-yjhtoi-api` (West US 2)
✅ **Resource Group**: `igshop-dev-rg-v2` 
✅ **Key Vault**: `igshop-dev-yjhtoi-kv`
✅ **Database**: `igshop-postgres` (Central US)
✅ **Static Web App**: `igshop-dev-yjhtoi-swa`

## 🚨 If Deployment Fails

1. Check GitHub Actions logs
2. Verify secrets are correctly added
3. Ensure Azure resources exist and are accessible
4. Check Key Vault permissions

## 📞 Need Help?

If you encounter issues:
1. Check the GitHub Actions logs for detailed error messages
2. Verify Azure CLI access: `az account show`
3. Test Azure resource access: `az webapp show --name igshop-dev-yjhtoi-api --resource-group igshop-dev-rg-v2` 