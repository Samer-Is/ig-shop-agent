# Instagram Page Connection Guide

## 1. Meta App Webhook Configuration

Go to your Meta App at [developers.facebook.com](https://developers.facebook.com)

### Messenger Webhooks:
1. Go to **Messenger** → **Settings**
2. Set **Callback URL**: `https://igshop-dev-functions-v2.azurewebsites.net/api/webhook/instagram`
3. Set **Verify Token**: `igshop_webhook_verify_2024`
4. Click **Verify and Save**

### Subscribe to Events:
- ✅ `messages` (essential for DM automation)
- ✅ `messaging_postbacks` (for button interactions)
- ✅ `message_deliveries` (for delivery status)

## 2. Instagram Page Connection

### Add Your Instagram Page:
1. Go to **Instagram** → **Basic Display**
2. Click **Add Instagram Account**
3. Login with your Instagram business account
4. Select your Instagram page from the dropdown
5. Authorize the connection

### Page Access Tokens:
1. Go to **Messenger** → **Settings**
2. In **Access Tokens** section
3. Select your Instagram page
4. Generate **Page Access Token**
5. **IMPORTANT**: Save this token - you'll need it for sending messages

## 3. Test User Setup

Since your page is already in testers:

1. Go to **Roles** → **Test Users**
2. Add Instagram accounts that can test DM automation
3. These users can send messages to your Instagram page
4. Messages will trigger your webhook

## 4. Testing the Integration

### Test Message Flow:
1. Have a test user send a DM to your Instagram page
2. Check your Function App logs to see webhook received
3. Your IG Shop Agent should process the message
4. Respond with product catalog or appropriate response

### Webhook Verification:
- ✅ Your webhook URL is verified and working
- ✅ Token `igshop_webhook_verify_2024` is correct
- ✅ All endpoints are operational

## 5. What Your IG Shop Agent Can Do Now

✅ **Receive Instagram DMs** via webhook  
✅ **Process Arabic product inquiries**  
✅ **Return product catalog** (قميص أبيض, بنطال جينز)  
✅ **Handle authentication** for admin features  
✅ **Scale to handle multiple customers**  

## 6. Next Steps for Production

1. **Get App Review**: Submit for Instagram Basic Display approval
2. **Go Live**: Switch from Development to Live mode
3. **Scale Up**: Handle unlimited Instagram accounts
4. **Analytics**: Track DM automation performance

## URLs Summary
- **Webhook URL**: `https://igshop-dev-functions-v2.azurewebsites.net/api/webhook/instagram`
- **Verify Token**: `igshop_webhook_verify_2024`
- **Health Check**: `https://igshop-dev-functions-v2.azurewebsites.net/api/health`
- **Product API**: `https://igshop-dev-functions-v2.azurewebsites.net/api/catalog` 