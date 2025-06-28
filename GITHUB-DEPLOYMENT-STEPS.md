# GitHub Deployment Steps

## 1. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ig-shop-agent` (or your preferred name)
3. Set to **Public** (required for free GitHub Actions)
4. **Don't** initialize with README, .gitignore, or license
5. Click "Create repository"

## 2. Add Remote and Push Code
After creating the repository, run these commands (replace YOUR_USERNAME with your GitHub username):

```bash
# Add GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/ig-shop-agent.git

# Push your existing code
git push -u origin master
```

## 3. Verify Deployment
After pushing, GitHub Actions will automatically:
1. Build your React frontend
2. Deploy to Azure Static Web Apps
3. The site will be live at your Azure Static Web App URL

## 4. Monitor Deployment
- Go to your GitHub repository → Actions tab
- Watch the "Azure Static Web Apps CI/CD" workflow
- If successful, your site will be deployed to Azure

## 5. Get Your Live URLs
Your application will be available at:
- **Frontend**: https://YOUR_STATIC_WEB_APP_NAME.2.azurestaticapps.net
- **Backend API**: Will be deployed separately via Azure Functions

## Troubleshooting
If deployment fails:
1. Check GitHub Actions logs
2. Verify your Azure Static Web App is properly configured
3. Ensure the API key in GitHub secrets is correct

## Next Steps
Once frontend is deployed:
1. Deploy backend via Azure Functions
2. Update frontend API endpoints
3. Configure Instagram webhook URLs
4. Test end-to-end functionality 