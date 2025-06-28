# Build and Deploy Functional React Dashboard
Write-Host "🔧 Building Functional IG Shop Agent Dashboard..." -ForegroundColor Green

$dashboardDir = "ig-shop-agent-dashboard"
$distDir = "$dashboardDir/dist"

# Check if we're in the right directory
if (-not (Test-Path $dashboardDir)) {
    Write-Host "❌ Dashboard directory not found: $dashboardDir" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found dashboard directory" -ForegroundColor Green

# Navigate to dashboard directory
Set-Location $dashboardDir

# Check if Node.js is available (try different approaches)
$nodeAvailable = $false
$buildCommand = ""

Write-Host "🔍 Checking build environment..." -ForegroundColor Yellow

# Try to find Node.js
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
        $nodeAvailable = $true
        
        # Check if npm is available
        try {
            npm --version | Out-Null
            $buildCommand = "npm"
            Write-Host "✅ npm available" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ npm not available, checking pnpm..." -ForegroundColor Yellow
            try {
                pnpm --version | Out-Null
                $buildCommand = "pnpm"
                Write-Host "✅ pnpm available" -ForegroundColor Green
            } catch {
                Write-Host "❌ Neither npm nor pnpm available" -ForegroundColor Red
                $nodeAvailable = $false
            }
        }
    }
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
}

if (-not $nodeAvailable) {
    Write-Host "`n💡 Node.js not available. Using existing build..." -ForegroundColor Yellow
    Write-Host "   If you want to rebuild, install Node.js from https://nodejs.org" -ForegroundColor Cyan
    
    # Check if dist exists
    if (-not (Test-Path "dist")) {
        Write-Host "❌ No existing build found and cannot rebuild" -ForegroundColor Red
        Write-Host "   Please install Node.js and run:" -ForegroundColor Yellow
        Write-Host "   npm install && npm run build" -ForegroundColor Cyan
        Set-Location ..
        exit 1
    }
    
    Write-Host "✅ Using existing build in dist/" -ForegroundColor Green
} else {
    # Build the application
    Write-Host "`n🏗️ Building application with $buildCommand..." -ForegroundColor Yellow
    
    try {
        # Install dependencies
        Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
        if ($buildCommand -eq "npm") {
            npm install --silent
        } else {
            pnpm install --silent
        }
        
        # Build
        Write-Host "🔨 Building production bundle..." -ForegroundColor Cyan
        if ($buildCommand -eq "npm") {
            npm run build
        } else {
            pnpm run build
        }
        
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "⚠️ Using existing build if available..." -ForegroundColor Yellow
        
        if (-not (Test-Path "dist")) {
            Write-Host "❌ No build available" -ForegroundColor Red
            Set-Location ..
            exit 1
        }
    }
}

# Go back to root directory
Set-Location ..

# Create deployment package
$zipPath = "functional-dashboard-deploy.zip"
Write-Host "`n📦 Creating deployment package..." -ForegroundColor Yellow

try {
    # Remove old zip if exists
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }

    # Create zip from dist folder
    Compress-Archive -Path "$distDir/*" -DestinationPath $zipPath -Force
    Write-Host "✅ Created deployment package: $zipPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create deployment package: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# List what's in the package
Write-Host "`n📋 Package contents:" -ForegroundColor Cyan
Get-ChildItem $distDir | ForEach-Object { Write-Host "   📄 $($_.Name)" -ForegroundColor White }

Write-Host "`n🌐 DEPLOYMENT OPTIONS:" -ForegroundColor Magenta

Write-Host "`n📌 OPTION 1: Azure Portal Upload (Recommended)" -ForegroundColor Yellow
Write-Host "   1. Go to: https://portal.azure.com" -ForegroundColor White
Write-Host "   2. Search: 'red-island-0b863450f'" -ForegroundColor White
Write-Host "   3. Go to Static Web App → Browse files" -ForegroundColor White
Write-Host "   4. Delete existing files" -ForegroundColor White
Write-Host "   5. Upload contents of: $distDir" -ForegroundColor White
Write-Host "   6. Wait for deployment (2-3 minutes)" -ForegroundColor White
Write-Host "   7. Access: https://red-island-0b863450f.2.azurestaticapps.net/" -ForegroundColor White

Write-Host "`n📌 OPTION 2: Netlify Drag & Drop" -ForegroundColor Yellow
Write-Host "   1. Go to: https://netlify.com" -ForegroundColor White
Write-Host "   2. Drag folder: $distDir" -ForegroundColor White
Write-Host "   3. Get instant URL!" -ForegroundColor White

Write-Host "`n📌 OPTION 3: GitHub Pages" -ForegroundColor Yellow
Write-Host "   1. Create new GitHub repo" -ForegroundColor White
Write-Host "   2. Upload contents of: $distDir" -ForegroundColor White
Write-Host "   3. Enable Pages in Settings" -ForegroundColor White

Write-Host "`n🎯 FUNCTIONAL FEATURES:" -ForegroundColor Green
Write-Host "   ✅ Real backend connection to:" -ForegroundColor White
Write-Host "      https://igshop-dev-functions-v2.azurewebsites.net/api" -ForegroundColor Cyan
Write-Host "   ✅ Live product data (3 products)" -ForegroundColor White
Write-Host "   ✅ Real analytics from backend" -ForegroundColor White
Write-Host "   ✅ Instagram status monitoring" -ForegroundColor White
Write-Host "   ✅ Connection health checks" -ForegroundColor White
Write-Host "   ✅ Auto-refresh functionality" -ForegroundColor White
Write-Host "   ✅ Error handling & fallbacks" -ForegroundColor White

Write-Host "`n🎉 Functional Dashboard Ready for Deployment!" -ForegroundColor Green
Write-Host "   The dashboard will now connect to your working backend!" -ForegroundColor Cyan

# Cleanup option
Write-Host "`n🧹 Clean up deployment package? (y/n): " -ForegroundColor Gray -NoNewline
$cleanup = Read-Host
if ($cleanup.ToLower() -eq "y") {
    Remove-Item $zipPath -Force
    Write-Host "✅ Cleanup completed" -ForegroundColor Green
} 