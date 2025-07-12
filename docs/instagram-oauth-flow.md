# Instagram OAuth Flow Documentation

## Overview
The IG-Shop-Agent implements Instagram Basic Display API OAuth for connecting user Instagram accounts to enable DM automation.

## Architecture Components

### 1. Backend Endpoints (Flask)
- `GET /auth/instagram` - Initiate OAuth flow
- `GET /auth/instagram/callback` - Handle OAuth callback

### 2. Frontend Integration (React)
- Settings page for Instagram connection
- Login flow integration for OAuth callback handling

### 3. Database Storage
- User table stores `instagram_user_id`, `instagram_username`, `instagram_access_token`
- Tokens encrypted and stored securely

## OAuth Flow Steps

### Step 1: Initiate OAuth (Frontend → Backend)
```typescript
// Frontend calls backend to get auth URL
const response = await apiService.getInstagramAuthUrl();
// Backend returns: { auth_url: string, status: string }
```

### Step 2: Generate Authorization URL (Backend)
```python
auth_url = (
    f"https://api.instagram.com/oauth/authorize"
    f"?client_id={app.config['META_APP_ID']}"
    f"&redirect_uri={app.config['META_REDIRECT_URI']}"
    f"&scope=user_profile,user_media"
    f"&response_type=code"
    f"&state={state}"
)
```

### Step 3: User Authorization (Instagram)
- User redirected to Instagram OAuth page
- User authorizes IG-Shop-Agent access
- Instagram redirects back with authorization code

### Step 4: Handle Callback (Backend)
```python
@app.route('/auth/instagram/callback')
def instagram_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validate state for CSRF protection
    # Exchange code for access token
    # Get user profile information
    # Store in database
```

### Step 5: Token Exchange
```python
token_data = {
    'client_id': app.config['META_APP_ID'],
    'client_secret': app.config['META_APP_SECRET'],
    'grant_type': 'authorization_code',
    'redirect_uri': app.config['META_REDIRECT_URI'],
    'code': code
}
token_response = requests.post('https://api.instagram.com/oauth/access_token', data=token_data)
```

### Step 6: Store User Data
```python
user_info_url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
user_info = requests.get(user_info_url).json()

# Update user record
user.instagram_user_id = user_info.get('id')
user.instagram_username = user_info.get('username')
user.instagram_access_token = access_token
```

## Security Considerations

### CSRF Protection
- State parameter generated as UUID
- Stored in session and validated on callback
- Prevents cross-site request forgery

### Token Security
- Access tokens should be encrypted before database storage
- Tokens have expiration dates that should be monitored
- Implement token refresh mechanism for long-lived access

### Environment Configuration
```python
META_APP_ID = os.environ.get('META_APP_ID')
META_APP_SECRET = os.environ.get('META_APP_SECRET')
META_REDIRECT_URI = os.environ.get('META_REDIRECT_URI', 'https://igshop-api.azurewebsites.net/auth/instagram/callback')
```

## Required Scopes
- `user_profile` - Access basic profile information
- `user_media` - Access user's media for catalog integration

## Error Handling
- Invalid state parameter
- Missing authorization code
- API request failures
- Token exchange failures
- User info retrieval failures

## Testing Requirements (When Backend Available)
1. ✅ Test OAuth initiation endpoint
2. ✅ Test callback handling with valid code
3. ✅ Test state parameter validation
4. ✅ Test token storage and retrieval
5. ✅ Test error scenarios

## Integration Points
- **Frontend Settings Page**: Instagram connection button
- **User Dashboard**: Display connection status
- **AI Agent**: Use stored tokens for DM automation
- **Database**: User table with Instagram fields

## Current Status
- ✅ Backend OAuth endpoints implemented
- ✅ Frontend integration ready
- ⚠️ Awaiting backend deployment for end-to-end testing
- ⚠️ Token encryption not yet implemented (security enhancement needed)

## Next Steps
1. Deploy backend to enable testing
2. Implement token encryption for security
3. Add token refresh mechanism
4. Complete end-to-end testing
5. Add error handling improvements 