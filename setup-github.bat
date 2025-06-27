@echo off
echo 🚀 Setting up IG-Shop-Agent GitHub Repository...

REM Check for git installation
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git not found. Installing Git...
    winget install Git.Git
    echo ✅ Git installed. Please restart command prompt and run this script again.
    pause
    exit /b 1
)

echo ✅ Git found!

REM Initialize git repository
echo 📁 Initializing Git repository...
git init
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to initialize Git repository
    pause
    exit /b 1
)

REM Configure git
echo ⚙️ Configuring Git...
set /p USERNAME="Enter your GitHub username: "
set /p EMAIL="Enter your GitHub email: "

git config user.name "%USERNAME%"
git config user.email "%EMAIL%"

REM Add all files
echo 📦 Adding files to repository...
git add .

REM Initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit: IG-Shop-Agent ultra low-cost Instagram DM automation platform - Features: AI-powered Instagram DM automation with Jordanian Arabic support, Ultra low-cost architecture: $28-40/month (vs $800+/month), Complete SaaS platform with multi-tenant support"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create commit
    pause
    exit /b 1
)

echo ✅ Initial commit created

echo.
echo 🐙 Now let's create the GitHub repository...
echo Please follow these steps:
echo.
echo 1. Go to https://github.com/new
echo 2. Repository name: ig-shop-agent
echo 3. Description: Ultra Low-Cost Instagram DM Automation Platform with Jordanian Arabic Support
echo 4. Make it Public
echo 5. Don't initialize with README (we already have one)
echo 6. Click 'Create repository'
echo.
pause

REM Add remote and push
echo 🔗 Adding remote repository...
git remote add origin https://github.com/%USERNAME%/ig-shop-agent.git

REM Rename main branch
echo 🌿 Setting up main branch...
git branch -M main

REM Push to GitHub
echo 🚀 Pushing to GitHub...
echo You may need to authenticate with GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 SUCCESS! Repository pushed to GitHub!
    echo Repository URL: https://github.com/%USERNAME%/ig-shop-agent
    echo.
    echo 📋 Next Steps:
    echo 1. Your repository is now live at: https://github.com/%USERNAME%/ig-shop-agent
    echo 2. Open Azure Cloud Shell: https://portal.azure.com
    echo 3. Run this deployment command:
    echo    curl -sSL https://raw.githubusercontent.com/%USERNAME%/ig-shop-agent/main/deploy-minimal.sh ^| bash -s -- dev
    echo 4. Your platform will be live in 3-5 minutes!
    echo.
    echo 💰 Expected monthly cost: $28-40 (vs $800+ original)
    echo 🎯 95%% cost savings achieved!
) else (
    echo ❌ Failed to push to GitHub
    echo Please check your GitHub credentials and try again.
)

echo.
pause 