# 🔧 Azure CLI Quick Fix Guide

Your Azure CLI is installed but not recognized. Here's how to fix it in 2 minutes:

## 🎯 Quick Solutions (Try in Order)

### Solution 1: Restart PowerShell (Simplest)
1. **Close** this PowerShell window completely
2. **Open** a new PowerShell window as Administrator:
   - Press `Win + X`
   - Click "Windows PowerShell (Admin)"
3. **Navigate** to your project:
   ```powershell
   cd "C:\Users\samer.ismail\Desktop\minmax_agent"
   ```
4. **Test** Azure CLI:
   ```powershell
   az --version
   ```

### Solution 2: Manual PATH Fix (if Solution 1 fails)
1. **Find Azure CLI** - check these locations in File Explorer:
   - `C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin`
   - `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin`

2. **If found**, add to PATH:
   ```powershell
   $env:PATH += ";C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
   az --version
   ```

### Solution 3: Fresh Installation (if not found)
1. **Double-click** the `AzureCLI.msi` file in your project folder
2. **Follow installer** (just click Next/Install)
3. **Restart PowerShell** completely
4. **Test**: `az --version`

### Solution 4: Download Fresh Installer
If the MSI file is corrupted:
1. **Download**: https://aka.ms/installazurecliwindows
2. **Run installer**
3. **Restart PowerShell**
4. **Test**: `az --version`

## 🚀 Once Azure CLI Works

When `az --version` shows version info, you're ready to deploy:

```powershell
# Step 1: Login to Azure
az login

# Step 2: Deploy everything
./deploy-minimal.sh dev
```

## 🎉 Expected Results

After deployment (3-5 minutes):
- **Frontend**: `https://igshop-dev-app.azurestaticapps.net`
- **Backend**: `https://igshop-dev-functions.azurewebsites.net`
- **Cost**: $28-40/month (vs $800+ original)

## 🆘 If Still Not Working

### Alternative: Use Azure Portal Browser
1. **Go to**: https://portal.azure.com
2. **Click**: Cloud Shell icon (>_) in top bar
3. **Choose**: Bash
4. **Upload files**: Use the upload button to upload:
   - `deploy-minimal.sh`
   - `infra/main.bicep`
   - `infra/parameters.dev.json`
   - `backend/` folder
5. **Deploy**:
   ```bash
   chmod +x deploy-minimal.sh
   ./deploy-minimal.sh dev
   ```

---

**🎯 Bottom Line**: Azure CLI is probably installed but PATH needs refresh. Try Solution 1 first (restart PowerShell) - it fixes 90% of cases!

**After Azure CLI works, you're 3 minutes away from a live platform with 95% cost savings! 🚀** 