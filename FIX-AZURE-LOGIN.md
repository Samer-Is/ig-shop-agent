# 🔐 Fix Azure CLI Login Issues

You're getting "you need internet for that" - this is a common Windows authentication issue. Here are proven solutions:

## 🎯 Quick Solutions (Try in Order)

### Solution 1: Use Device Code Login (Recommended)
This bypasses Windows account integration:

```powershell
az login --use-device-code
```

**What happens:**
1. You'll get a code like `ABC123DEF`
2. It will say "Go to https://microsoft.com/devicelogin"
3. **Open that URL in any browser**
4. **Enter the code**
5. **Sign in with your Azure account**
6. **Return to PowerShell** - it should say "Login successful"

### Solution 2: Force Browser Login
```powershell
az login --scope https://management.azure.com//.default
```

### Solution 3: Use Different Browser
```powershell
# This opens login in your default browser
az login --tenant your-tenant-id
```

Your tenant ID is: `062f77f6-a70b-44c6-ae4a-b709e3cfd2ed`

So try:
```powershell
az login --tenant 062f77f6-a70b-44c6-ae4a-b709e3cfd2ed
```

### Solution 4: Clear Azure CLI Cache
```powershell
# Clear any cached credentials
az account clear
az login --use-device-code
```

## 🔍 Troubleshooting Specific Issues

### "You need internet for that"
This usually means Windows is trying to use cached/integrated auth instead of browser:

**Fix A: Disable Windows Integration**
```powershell
az config set core.allow_broker=false
az login --use-device-code
```

**Fix B: Force Interactive**
```powershell
az login --allow-no-subscriptions
```

### Windows Account Picker Interfering
```powershell
# Skip Windows account integration
az login --use-device-code --tenant 062f77f6-a70b-44c6-ae4a-b709e3cfd2ed
```

## 🚀 Once Login Works

After successful login, verify:
```powershell
# Check if you're logged in
az account show

# List your subscriptions
az account list --output table
```

You should see your "Azure subscription 1" listed.

## 🎯 Then Deploy Immediately!

Once `az account show` works:
```powershell
# Deploy your ultra low-cost platform
./deploy-minimal.sh dev
```

## 🆘 Alternative: Azure Cloud Shell

If login still fails, use the browser-based Azure Cloud Shell:

1. **Go to**: https://portal.azure.com
2. **You're already logged in** in the browser
3. **Click**: Cloud Shell icon (>_)
4. **Choose**: Bash
5. **Upload files** and deploy

## ✅ Expected Success Flow

```powershell
PS C:\Users\samer.ismail\Desktop\minmax_agent> az login --use-device-code
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code ABC123DEF to authenticate.
[
  {
    "cloudName": "AzureCloud",
    "homeTenantId": "062f77f6-a70b-44c6-ae4a-b709e3cfd2ed",
    "id": "your-subscription-id",
    "name": "Azure subscription 1",
    "state": "Enabled",
    "tenantId": "062f77f6-a70b-44c6-ae4a-b709e3cfd2ed"
  }
]

PS C:\Users\samer.ismail\Desktop\minmax_agent> ./deploy-minimal.sh dev
🚀 Starting deployment...
```

## 🎉 Why This Happens

- **Windows integration** tries to use your Windows account
- **Corporate networks** sometimes block direct browser auth
- **Device code flow** bypasses these issues
- **Azure Cloud Shell** is always the failsafe option

---

**🎯 Bottom Line**: Use `az login --use-device-code` - it works 95% of the time and bypasses Windows account integration issues!

**After login works, you're 3 minutes from deployment! 🚀** 