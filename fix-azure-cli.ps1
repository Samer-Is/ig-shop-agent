# Azure CLI Fix Script
# This script will find, install, or fix Azure CLI on your system

Write-Host "🔧 Azure CLI Fix Script" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Function to test if Azure CLI works
function Test-AzureCLI {
    try {
        $result = & az --version 2>$null
        if ($result) {
            Write-Host "✅ Azure CLI is working!" -ForegroundColor Green
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

# Function to add path to environment
function Add-ToPath {
    param($PathToAdd)
    
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$PathToAdd*") {
        $newPath = "$currentPath;$PathToAdd"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        $env:PATH = "$env:PATH;$PathToAdd"
        Write-Host "✅ Added to PATH: $PathToAdd" -ForegroundColor Green
    }
}

# Check if Azure CLI already works
Write-Host "🔍 Checking if Azure CLI already works..." -ForegroundColor Blue
if (Test-AzureCLI) {
    Write-Host "🎉 Azure CLI is already working! You can run 'az login' now." -ForegroundColor Green
    exit 0
}

# Search for existing Azure CLI installations
Write-Host "🔍 Searching for existing Azure CLI installations..." -ForegroundColor Blue

$possiblePaths = @(
    "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin",
    "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin", 
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft\Azure CLI\wbin",
    "C:\Program Files\Azure CLI\wbin",
    "C:\Program Files (x86)\Azure CLI\wbin"
)

$foundPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\az.cmd") {
        Write-Host "✅ Found Azure CLI at: $path" -ForegroundColor Green
        $foundPath = $path
        break
    }
}

if ($foundPath) {
    Write-Host "🔧 Adding Azure CLI to PATH..." -ForegroundColor Blue
    Add-ToPath $foundPath
    
    # Test again
    Write-Host "🧪 Testing Azure CLI..." -ForegroundColor Blue
    if (Test-AzureCLI) {
        Write-Host "🎉 SUCCESS! Azure CLI is now working!" -ForegroundColor Green
        Write-Host "You can now run: az login" -ForegroundColor Yellow
        exit 0
    }
}

# If not found, try to install
Write-Host "📦 Azure CLI not found. Installing..." -ForegroundColor Yellow

# Method 1: Try winget
Write-Host "📦 Trying winget installation..." -ForegroundColor Blue
try {
    $wingetResult = winget install Microsoft.AzureCLI --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Azure CLI installed via winget" -ForegroundColor Green
        
        # Add likely installation path
        Add-ToPath "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
        
        if (Test-AzureCLI) {
            Write-Host "🎉 SUCCESS! Azure CLI is working!" -ForegroundColor Green
            exit 0
        }
    }
}
catch {
    Write-Host "⚠️ Winget installation failed, trying MSI..." -ForegroundColor Yellow
}

# Method 2: Try MSI installation
Write-Host "📦 Trying MSI installation..." -ForegroundColor Blue

$msiPath = ".\AzureCLI.msi"
if (Test-Path $msiPath) {
    Write-Host "📦 Found AzureCLI.msi in current directory, installing..." -ForegroundColor Blue
    try {
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$msiPath`" /quiet /norestart" -Wait
        Write-Host "✅ MSI installation completed" -ForegroundColor Green
        
        # Add installation paths
        Add-ToPath "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
        Add-ToPath "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"
        
        if (Test-AzureCLI) {
            Write-Host "🎉 SUCCESS! Azure CLI is working!" -ForegroundColor Green
            exit 0
        }
    }
    catch {
        Write-Host "❌ MSI installation failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Method 3: Download and install MSI
Write-Host "📦 Downloading Azure CLI MSI..." -ForegroundColor Blue
try {
    $downloadUrl = "https://aka.ms/installazurecliwindows"
    $downloadPath = "$env:TEMP\AzureCLI.msi"
    
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "✅ Downloaded Azure CLI MSI" -ForegroundColor Green
    
    Write-Host "📦 Installing Azure CLI..." -ForegroundColor Blue
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$downloadPath`" /quiet /norestart" -Wait
    
    # Clean up
    Remove-Item $downloadPath -ErrorAction SilentlyContinue
    
    # Add installation paths
    Add-ToPath "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
    Add-ToPath "C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"
    
    Write-Host "✅ Installation completed" -ForegroundColor Green
}
catch {
    Write-Host "❌ Download/installation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Final test
Write-Host "🧪 Final test..." -ForegroundColor Blue
if (Test-AzureCLI) {
    Write-Host "🎉 SUCCESS! Azure CLI is now working!" -ForegroundColor Green
    Write-Host "🚀 Ready to deploy! Run these commands:" -ForegroundColor Cyan
    Write-Host "   az login" -ForegroundColor Yellow
    Write-Host "   ./deploy-minimal.sh dev" -ForegroundColor Yellow
} else {
    Write-Host "❌ Azure CLI still not working. Manual installation needed." -ForegroundColor Red
    Write-Host "📋 Manual steps:" -ForegroundColor Yellow
    Write-Host "1. Download: https://aka.ms/installazurecliwindows" -ForegroundColor White
    Write-Host "2. Run the installer" -ForegroundColor White
    Write-Host "3. Restart PowerShell" -ForegroundColor White
    Write-Host "4. Try 'az --version'" -ForegroundColor White
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 