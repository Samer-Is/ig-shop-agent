@echo off
echo 🔧 Azure CLI Quick Fix
echo =====================

REM Test if Azure CLI already works
echo 🔍 Testing if Azure CLI works...
az --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Azure CLI is already working!
    echo 🚀 You can run: az login
    goto :end
)

echo ❌ Azure CLI not working, trying to fix...

REM Try to find and add Azure CLI to PATH
echo 🔍 Searching for Azure CLI installation...

if exist "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
    echo ✅ Found Azure CLI, adding to PATH...
    set "PATH=%PATH%;C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
    goto :test
)

if exist "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" (
    echo ✅ Found Azure CLI, adding to PATH...
    set "PATH=%PATH%;C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"
    goto :test
)

REM If not found, try to install
echo 📦 Azure CLI not found, installing...

REM Try using existing MSI file
if exist "AzureCLI.msi" (
    echo 📦 Installing from AzureCLI.msi...
    msiexec /i "AzureCLI.msi" /quiet /norestart
    echo ✅ Installation completed
    set "PATH=%PATH%;C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
    goto :test
)

REM Try winget installation
echo 📦 Trying winget installation...
winget install Microsoft.AzureCLI --silent
if %ERRORLEVEL% EQU 0 (
    echo ✅ Installed via winget
    set "PATH=%PATH%;C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
    goto :test
)

echo ❌ Automatic installation failed
echo 📋 Manual installation needed:
echo 1. Download: https://aka.ms/installazurecliwindows
echo 2. Run the installer
echo 3. Restart command prompt
echo 4. Try 'az --version'
goto :end

:test
echo 🧪 Testing Azure CLI...
az --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo 🎉 SUCCESS! Azure CLI is now working!
    echo.
    echo 🚀 Next steps:
    echo    az login
    echo    ./deploy-minimal.sh dev
    echo.
    echo 💰 Your platform will be live in 3-5 minutes with $28-40/month cost!
) else (
    echo ❌ Still not working. Please restart command prompt and try again.
    echo Or run the PowerShell version: fix-azure-cli.ps1
)

:end
echo.
pause 