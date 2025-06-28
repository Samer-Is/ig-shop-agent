# Deploy Frontend to Azure Static Web App

## Current Status
✅ Azure Static Web App created successfully:
- **Name**: `igshop-dev-webapp`
- **URL**: `https://red-island-0b863450f.2.azurestaticapps.net`
- **Resource Group**: `igshop-dev-rg-v2`
- **SKU**: Free

## Deployment Options

### Option A: GitHub Actions (Recommended)

#### Step 1: Create GitHub Repository
1. Go to [GitHub](https://github.com/new)
2. Create a **private** repository named `ig-shop-agent`
3. Don't initialize with README

#### Step 2: Connect Static Web App to GitHub
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Resource Groups → `igshop-dev-rg-v2` → `igshop-dev-webapp`
3. In the left menu, click **"Deployment" → "GitHub Actions"**
4. Click **"Connect to GitHub"**
5. Authorize Azure to access your GitHub account
6. Select your repository: `ig-shop-agent`
7. Branch: `main` or `master`
8. Build presets: **React**
9. App location: `/ig-shop-agent-dashboard`
10. Output location: `dist`

#### Step 3: Push Code to GitHub
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/ig-shop-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

#### Step 4: Automatic Deployment
Once you push to GitHub, Azure will automatically:
- Detect the React app in `/ig-shop-agent-dashboard`
- Build the app using `npm run build`
- Deploy to your Static Web App
- Your site will be live at: `https://red-island-0b863450f.2.azurestaticapps.net`

### Option B: Manual Upload via Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Resource Groups → `igshop-dev-rg-v2` → `igshop-dev-webapp`
3. Click **"Deployment" → "Browse"**
4. Upload the contents of `ig-shop-agent-dashboard/dist/` folder
   - Upload `index.html`
   - Upload `assets/` folder
   - Upload `images/` folder

### Option C: Azure Static Web Apps CLI

If you want to use CLI deployment:

```bash
# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# Get deployment token
az staticwebapp secrets list --resource-group "igshop-dev-rg-v2" --name "igshop-dev-webapp"

# Deploy
swa deploy --app-location ig-shop-agent-dashboard/dist --deployment-token YOUR_DEPLOYMENT_TOKEN
```

## Next Steps After Deployment

### 1. Update API Endpoints
Once deployed, update the frontend to point to your Function App:
- Function App URL: `https://igshop-dev-functions-v2.azurewebsites.net`

### 2. Configure CORS
Enable CORS on your Function App to allow requests from the Static Web App:
```bash
az functionapp cors add --resource-group "igshop-dev-rg-v2" --name "igshop-dev-functions-v2" --allowed-origins "https://red-island-0b863450f.2.azurestaticapps.net"
```

### 3. Test the Complete Application
- Frontend: `https://red-island-0b863450f.2.azurestaticapps.net`
- Backend API: `https://igshop-dev-functions-v2.azurewebsites.net`

## Troubleshooting

### If GitHub Actions Fails
- Check the Actions tab in your GitHub repository
- Common issues:
  - Wrong app location path
  - Missing package.json in the app location
  - Build errors

### If Manual Upload Doesn't Work
- Ensure you're uploading the built files from `dist/` folder
- Check that `index.html` is in the root

### If CLI Deployment Fails
- Verify the deployment token is correct
- Ensure SWA CLI is installed globally
- Check that you're in the correct directory

## Cost Breakdown
- Azure Static Web App (Free tier): **$0/month**
- Perfect for our ultra low-cost architecture!

## Security Notes
- Static Web App includes:
  - Free SSL certificate
  - CDN for global performance
  - Custom domains support
  - Authentication integration

Total cost impact: **$0** (Free tier is sufficient for development and small-scale production) 