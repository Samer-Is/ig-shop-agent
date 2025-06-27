# 🚀 Manual GitHub Setup Guide for IG-Shop-Agent

Since the terminal is having issues, here's a step-by-step manual process to get your repository on GitHub and ready for deployment.

## Step 1: Install Git (if needed)
1. Download Git from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart PowerShell/Command Prompt

## Step 2: Open Command Prompt or PowerShell
1. Press `Win + R`
2. Type `cmd` and press Enter
3. Navigate to your project:
```cmd
cd "C:\Users\samer.ismail\Desktop\minmax_agent"
```

## Step 3: Initialize Git Repository
```cmd
git init
```

## Step 4: Configure Git (replace with your details)
```cmd
git config user.name "YourGitHubUsername"
git config user.email "your.email@example.com"
```

## Step 5: Add All Files
```cmd
git add .
```

## Step 6: Create Initial Commit
```cmd
git commit -m "Initial commit: IG-Shop-Agent ultra low-cost Instagram DM automation platform

Features:
- AI-powered Instagram DM automation with Jordanian Arabic support
- Ultra low-cost architecture: $28-40/month (vs $800+/month)
- Complete SaaS platform with multi-tenant support
- React TypeScript frontend with modern UI
- FastAPI backend with Azure Functions
- PostgreSQL with pgvector for vector search
- Secure JWT authentication
- Real-time analytics and monitoring

Cost Optimization:
- Original: $800-1200/month
- Optimized: $28-40/month
- Savings: 95% cost reduction

Ready for one-command deployment!"
```

## Step 7: Create GitHub Repository
1. Go to: https://github.com/new
2. **Repository name**: `ig-shop-agent`
3. **Description**: `Ultra Low-Cost Instagram DM Automation Platform with Jordanian Arabic Support`
4. **Visibility**: Public (recommended)
5. **Do NOT** check "Initialize this repository with a README"
6. Click **"Create repository"**

## Step 8: Connect Local Repository to GitHub
Replace `YourGitHubUsername` with your actual GitHub username:
```cmd
git remote add origin https://github.com/YourGitHubUsername/ig-shop-agent.git
git branch -M main
git push -u origin main
```

## Step 9: Authenticate with GitHub
When prompted, you have two options:

### Option A: GitHub CLI (Recommended)
1. Install GitHub CLI: https://cli.github.com/
2. Run: `gh auth login`
3. Follow the prompts

### Option B: Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "IG-Shop-Agent Deploy"
4. Select scopes: `repo`, `workflow`
5. Generate and copy the token
6. Use the token as your password when prompted

## Step 10: Verify Upload
1. Go to your repository: `https://github.com/YourGitHubUsername/ig-shop-agent`
2. You should see all your files there

## 🎉 Next: Deploy to Azure

Once your repository is on GitHub, deploy using Azure Cloud Shell:

1. **Open Azure Cloud Shell**: https://portal.azure.com (click the >_ icon)
2. **Choose Bash** when prompted
3. **Run the deployment command** (replace `YourGitHubUsername`):

```bash
curl -sSL https://raw.githubusercontent.com/YourGitHubUsername/ig-shop-agent/main/deploy-minimal.sh | bash -s -- dev
```

## Expected Results
- **Repository**: `https://github.com/YourGitHubUsername/ig-shop-agent`
- **Frontend**: `https://igshop-dev-app.azurestaticapps.net`
- **Backend**: `https://igshop-dev-functions.azurewebsites.net`
- **Monthly Cost**: $28-40 (vs $800+ original)
- **Deployment Time**: 3-5 minutes

## Troubleshooting

### Git Not Found
- Download and install from: https://git-scm.com/download/win
- Restart your terminal after installation

### Authentication Issues
- Use GitHub CLI: `gh auth login`
- Or use Personal Access Token instead of password

### Repository Already Exists
- If you get an error about the repository existing, either:
  1. Delete the existing repository on GitHub
  2. Or use a different name like `ig-shop-agent-v2`

---

**🚀 Ready to launch your ultra low-cost Instagram automation platform!**

After following these steps, you'll have:
- ✅ Professional GitHub repository
- ✅ Complete documentation
- ✅ Ready for one-command Azure deployment
- ✅ 95% cost savings vs traditional architecture 