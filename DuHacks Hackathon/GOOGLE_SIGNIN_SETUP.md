# 🔐 Google Sign-In Setup Guide

## Overview
Your application now includes **Google Sign-In OAuth 2.0** authentication. Users can sign in or sign up using their Google accounts.

## Quick Setup (3 Steps)

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the **Google+ API**

### Step 2: Create OAuth 2.0 Credentials
1. Go to **Credentials** in the left sidebar
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Web application**
4. Add authorized redirect URIs:
   - `http://localhost:9000`
   - `http://localhost:8000`
   - `http://127.0.0.1:9000`
5. Copy your **Client ID**

### Step 3: Add Client ID to Your App
Edit `script.js` and replace this line:
```javascript
client_id: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
```

With your actual Client ID:
```javascript
client_id: '123456789-abcdefgh.apps.googleusercontent.com',
```

## Files Involved

### 1. **index.html**
- Contains the Google Sign-In script tag: `<script src="https://accounts.google.com/gsi/client" async defer></script>`
- Has Google Sign-In buttons on login and signup pages with IDs:
  - `googleSignInButton` (Login page)
  - `googleSignUpButton` (Signup page)

### 2. **script.js**
- `initializeGoogleSignIn()` - Initializes the Google Sign-In API
- `handleGoogleSignInResponse(response)` - Processes the Google response
- `signInWithGoogle()` - Triggers sign-in
- `signUpWithGoogle()` - Triggers sign-up

## How It Works

### User Flow
1. User clicks "Sign in with Google" button
2. Google One Tap or popup appears
3. User selects their Google account
4. JWT token is sent to your app
5. Token is decoded to extract user info
6. User is logged in and redirected to dashboard

### Behind the Scenes
```javascript
// 1. Google returns JWT token
const response = {
    credential: "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0..."
}

// 2. Token is decoded
const data = {
    sub: "1234567890",           // Google user ID
    email: "user@gmail.com",     // Email
    name: "John Doe",            // Full name
    picture: "https://...",      // Avatar URL
}

// 3. User object created
const user = {
    id: 'google_1234567890',
    email: 'user@gmail.com',
    name: 'John Doe',
    avatar: 'https://...',
    loginMethod: 'google',
    googleId: '1234567890'
}

// 4. User logged in
loginUser(user);
```

## Configuration

### Customize Button Appearance
In `script.js`, find the `renderButton` calls and modify options:

```javascript
// For login page
google.accounts.id.renderButton(loginButton, {
    theme: 'outline',      // 'outline', 'filled_blue', 'filled_black'
    size: 'large',         // 'large', 'medium', 'small'
    text: 'signin_with',   // 'signin_with', 'signup_with', 'continue_with'
});

// For signup page
google.accounts.id.renderButton(signupButton, {
    theme: 'outline',
    size: 'large',
    text: 'signup_with',
});
```

### One Tap UI
The Google One Tap prompt automatically shows when page loads. To disable:
```javascript
// In initializeGoogleSignIn()
// Comment out or remove:
// window.google.accounts.id.prompt((notification) => { ... });
```

## Security Best Practices

✅ **DO:**
- Keep your Client ID in a safe place
- Use HTTPS in production
- Validate tokens on your backend (if applicable)
- Store auth tokens in `localStorage` securely
- Clear tokens on logout

❌ **DON'T:**
- Commit Client Secret to git
- Expose backend secrets in frontend code
- Use Client ID with secret in frontend
- Trust client-side validation alone

## Testing

### Test Google Sign-In
1. Start your web server: `python web_server.py`
2. Open http://localhost:9000 in browser
3. Click "Sign in with Google" or "Sign up with Google"
4. Select a Google account
5. You should see: ✅ Welcome notification
6. Redirected to dashboard

### Check Console
Open browser DevTools (F12) and check:
- ✅ "Google Sign-In initialized" - Setup successful
- ✅ "Google Sign-In response received" - Login worked
- ❌ "Error initializing Google Sign-In" - Check Client ID
- ❌ "Error processing Google Sign-In" - Check JWT decode

## Troubleshooting

### Problem: "Google is not defined"
**Solution:** Make sure Google Sign-In script is loaded in HTML head:
```html
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

### Problem: "redirect_uri_mismatch"
**Solution:** Add your redirect URIs in Google Cloud Console credentials

### Problem: Button not showing
**Solution:** 
1. Check browser console for errors
2. Verify Client ID is correct
3. Try hardrefresh (Ctrl+F5)
4. Check that `googleSignInButton` or `googleSignUpButton` IDs exist in HTML

### Problem: Token validation fails
**Solution:**
1. Ensure you're decoding JWT correctly
2. Check token format (should be 3 parts separated by dots)
3. Verify token is not expired

## Advanced: Custom OAuth Server

For production, you may want to:
1. Create a backend OAuth server
2. Exchange JWT tokens for your own auth tokens
3. Store user data in database
4. Manage sessions server-side

Example backend endpoint:
```python
@app.post("/auth/google")
async def auth_google(token: str):
    # Verify Google JWT token
    # Check token signature and expiration
    # Create/update user in database
    # Return your own auth token
    pass
```

## Links & Resources

- 📚 [Google Sign-In Documentation](https://developers.google.com/identity/gsi/web)
- 🔐 [Google Cloud Console](https://console.cloud.google.com)
- 📖 [OAuth 2.0 Overview](https://developers.google.com/identity/protocols/oauth2)
- 🛡️ [JWT Token Format](https://jwt.io)
- 🔑 [Google API Keys](https://developers.google.com/identity/protocols/OAuth2ServiceAccount)

## Support

If you encounter issues:
1. Check the [Google Sign-In troubleshooting guide](https://developers.google.com/identity/gsi/web/guides/get-started)
2. Review browser console for error messages
3. Verify Client ID and redirect URIs match
4. Try incognito/private browsing mode

---

**Your Google Sign-In is now configured and ready to use! 🎉**
