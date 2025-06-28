# 🚀 IG Shop Agent - Complete Quick Start Guide

## 📋 What You'll Get
- ✅ **Working Frontend Dashboard** with Instagram OAuth button
- ✅ **AI Agent Backend** processing customer messages in Arabic & English
- ✅ **Instagram DM Integration** ready for real customers
- ✅ **Analytics Dashboard** with live customer data

---

## 🏃‍♂️ OPTION 1: Quick Local Test (2 minutes)

### **Step 1: Start Frontend Locally**
```powershell
# In your project directory
.\run-frontend-local.ps1
```

### **Step 2: Open Browser**
```
http://localhost:8000
```

### **Step 3: Test Features**
- ✅ Click "Connect to Instagram" button
- ✅ Test AI Agent with messages like "مرحبا أريد قميص"
- ✅ View analytics dashboard
- ✅ Check product catalog

**Backend is already deployed and working at:**
`https://igshop-dev-functions-v2.azurewebsites.net`

---

## 🌐 OPTION 2: Deploy Frontend to Cloud (5 minutes)

### **Method A: GitHub Pages (Free)**

1. **Create GitHub Repository**
   ```bash
   # Create new repo on GitHub called "igshop-frontend"
   ```

2. **Upload Frontend Files**
   ```bash
   git init
   git add frontend/*
   git commit -m "IG Shop Agent Frontend"
   git remote add origin https://github.com/YOUR_USERNAME/igshop-frontend.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to repository Settings
   - Scroll to "Pages" section
   - Source: Deploy from branch "main" 
   - Folder: "/ (root)"
   - Save

4. **Access Your Live Site**
   ```
   https://YOUR_USERNAME.github.io/igshop-frontend/
   ```

### **Method B: Netlify (Free)**

1. **Go to** https://netlify.com
2. **Drag & Drop** the `frontend` folder
3. **Get instant URL** like `https://amazing-name-123.netlify.app`

### **Method C: Azure Static Web Apps**

1. **Create Static Web App**
   ```bash
   az staticwebapp create \
     --name "igshop-frontend" \
     --resource-group "igshop-dev-rg-v2" \
     --location "Central US"
   ```

2. **Upload Files**
   ```bash
   # Use Azure CLI or portal to upload frontend files
   ```

---

## 🔗 BACKEND STATUS (Already Working!)

### **✅ Current Backend Features**
```
Backend URL: https://igshop-dev-functions-v2.azurewebsites.net
Status: ✅ LIVE & WORKING
Version: 2.0.0

Features:
✅ AI Agent (Arabic/English)
✅ Product Catalog (3 products)
✅ Instagram OAuth endpoints
✅ Webhook system ready
✅ Analytics & customer database
✅ Message processing
```

### **Test Backend APIs**
```powershell
# Health Check
Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/health"

# Product Catalog  
Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/catalog"

# Test AI Agent
$testMessage = @{ message = "مرحبا أريد قميص" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/ai/test-response" -Method POST -Body $testMessage -ContentType "application/json"
```

---

## 📱 INSTAGRAM INTEGRATION (Final Step)

### **When Ready for Real Customers:**

1. **Create Instagram App**
   - Go to https://developers.facebook.com
   - Create new app → Business → Instagram Basic Display
   - Get App ID and App Secret

2. **Configure Webhook**
   ```
   Webhook URL: https://igshop-dev-functions-v2.azurewebsites.net/api/webhook/instagram
   Verify Token: igshop_webhook_verify_2024
   Subscribe to: messages
   ```

3. **Update Backend Environment**
   ```bash
   az functionapp config appsettings set \
     --resource-group igshop-dev-rg-v2 \
     --name igshop-dev-functions-v2 \
     --settings INSTAGRAM_APP_ID=your_real_app_id INSTAGRAM_APP_SECRET=your_real_secret
   ```

4. **Test Real DMs**
   - Send message to your Instagram page
   - AI will respond automatically!

---

## 🛠️ TROUBLESHOOTING

### **Frontend Not Loading?**
```powershell
# Check if files exist
ls frontend/
# Should show: index.html, app.js, oauth-callback.html

# Try different browser
# Check browser console for errors (F12)
```

### **Backend Not Responding?**
```powershell
# Test health endpoint
Invoke-RestMethod -Uri "https://igshop-dev-functions-v2.azurewebsites.net/api/health"

# Restart function app if needed
az functionapp restart --resource-group igshop-dev-rg-v2 --name igshop-dev-functions-v2
```

### **Instagram OAuth Not Working?**
- Update Instagram app credentials in backend
- Check redirect URIs in Instagram app settings
- Verify webhook URL is accessible

---

## 🎯 SUCCESS CHECKLIST

### **Frontend Working ✅**
- [ ] Can access dashboard in browser
- [ ] "Connect to Instagram" button visible
- [ ] AI test section functional
- [ ] Analytics dashboard displays
- [ ] Product catalog shows 3 items

### **Backend Working ✅**
- [ ] Health endpoint returns "healthy"
- [ ] AI agent responds to test messages
- [ ] Webhook verification passes
- [ ] Analytics endpoint returns data
- [ ] Product catalog has Arabic names

### **Ready for Customers ✅**
- [ ] Instagram app configured
- [ ] Webhook URL set in Meta console
- [ ] Real DM test successful
- [ ] AI responds to customer messages
- [ ] Analytics tracking customer interactions

---

## 🎉 YOU'RE READY!

Your **complete IG Shop Agent** is now running with:

🤖 **AI Customer Service** - Automatic responses in Arabic & English  
📱 **Instagram Integration** - Real DM automation  
📊 **Analytics Dashboard** - Customer insights & metrics  
🛍️ **Product Catalog** - Inventory management  
🔗 **Modern Frontend** - Professional admin dashboard  

**Start with Option 1 (local test) to see everything working, then deploy with Option 2 for live access!** 