# ⚡ Quick Reference - Google Sign-In & Full Auth

## 🚀 Start Here

```bash
# 1. Run web server
python web_server.py

# 2. Open browser
http://localhost:9000

# 3. Try email signup (no setup needed)
# 4. Or add Google Client ID for OAuth
```

---

## 🔐 Authentication Methods

### Email/Password ✅ Ready
```javascript
// Already working!
// Form: script.js handles it automatically
// No setup needed
```

**Test:**
- Click "Sign up"
- Enter: name, email, password (8+ chars)
- Click "Create Account"

---

### Google Sign-In ✅ Integrated (Need Client ID)

**1-Minute Setup:**
1. Go to https://console.cloud.google.com
2. OAuth credentials → Web → Copy Client ID
3. Edit `script.js` line 732:
   ```javascript
   // Change this:
   client_id: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
   
   // To this:
   client_id: 'YOUR-ACTUAL-ID-123456.apps.googleusercontent.com',
   ```
4. Reload http://localhost:9000
5. Click "Sign in with Google" ✅

**What Happens:**
```
User clicks button 
→ Google dialog appears 
→ Selects account 
→ JWT token sent to app 
→ Token decoded 
→ User logged in ✅
```

---

### Spotify ✅ Integrated (Need Credentials)

**Setup:**
1. Create app: https://developer.spotify.com/dashboard
2. Get Client ID & Secret
3. Set env vars:
   ```powershell
   $env:SPOTIFY_CLIENT_ID="your_id"
   $env:SPOTIFY_CLIENT_SECRET="your_secret"
   ```
4. Start backend:
   ```bash
   python backend_api.py
   ```
5. Click "Sign in with Spotify" ✅

---

## 📂 Key Files

| File | Purpose | What to Change |
|------|---------|---|
| `script.js:732` | Google OAuth init | Add your Client ID |
| `index.html:9` | Google script tag | ✅ Already there |
| `index.html:50` | Google login button | ✅ Already there |
| `.env` or terminal | Spotify creds | Set env vars |

---

## 🎯 What's Configured

```
✅ Google Sign-In script loaded
✅ Google login button in HTML
✅ Google signup button in HTML
✅ JWT token decoder in JS
✅ User creation after Google login
✅ localStorage for user data
✅ Logout functionality
✅ Email/password forms
✅ Spotify buttons
✅ Spotify search API
✅ Backend API running
```

---

## 🧪 Test It

### Email Auth
```
http://localhost:9000
→ Sign Up
→ Fill form
→ Create Account
→ ✅ See dashboard
```

### Google Auth (after setup)
```
http://localhost:9000
→ Click "Sign in with Google"
→ Select account
→ ✅ See dashboard
```

### Console Test
```javascript
// Open DevTools (F12)
// Google Sign-In status
console.log('Google:', window.google ? '✅ Loaded' : '❌ Not loaded')

// Search Spotify
await spotifySearchTracks('lo-fi')
```

---

## 📊 Data Flow

```
Browser
  ↓
HTML (buttons + form)
  ↓
JavaScript (script.js)
  ├→ handleLogin() [email]
  ├→ handleGoogleSignInResponse() [Google JWT]
  ├→ signInWithSpotify() [Spotify]
  ↓
localStorage
  └→ User data stored
  ↓
showDashboard()
```

---

## 🔑 Getting Credentials

### Google Client ID
**Time: 5 mins**

```
1. console.cloud.google.com
2. Create Project
3. Credentials → Create → OAuth 2.0 → Web
4. Add Authorized redirect URI:
   http://localhost:9000
   http://localhost:8000
5. Copy "Client ID"
6. Add to script.js line 732
```

### Spotify Client ID & Secret
**Time: 5 mins**

```
1. developer.spotify.com/dashboard
2. Create an App
3. Accept terms
4. Copy "Client ID"
5. Copy "Client Secret"
6. Set environment variables:
   $env:SPOTIFY_CLIENT_ID = "..."
   $env:SPOTIFY_CLIENT_SECRET = "..."
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Google button not showing | Hard refresh (Ctrl+F5) |
| "Google is not defined" | Check script tag in head |
| Google auth fails | Verify Client ID is correct |
| Redirect URI mismatch | Add http://localhost:9000 in OAuth settings |
| Spotify not working | Check env vars are set, backend is running |
| Form won't submit | Check password is 8+ characters |

---

## 📝 Code Snippets

### Check if Google is loaded
```javascript
if (window.google && window.google.accounts) {
    console.log('✅ Google API loaded');
} else {
    console.log('❌ Google API not loaded');
}
```

### Manually trigger Google sign-in
```javascript
window.google.accounts.id.prompt();
```

### Get current user
```javascript
const user = JSON.parse(localStorage.getItem('musicai_user'));
console.log(user.name, user.email, user.loginMethod);
```

### Sign out
```javascript
logout(); // or
localStorage.clear();
location.reload();
```

---

## 📚 Full Documentation

For complete details, see:
- `GOOGLE_SIGNIN_SETUP.md` - Full Google setup guide
- `AUTH_STATUS.md` - All auth methods explained
- `INTEGRATION_COMPLETE.md` - Complete system overview
- `SPOTIFY_SETUP.md` - Spotify integration guide

---

## ✅ Checklist

- [ ] Opened http://localhost:9000
- [ ] Tested email/password signup ✅
- [ ] Got Google Client ID
- [ ] Added Client ID to script.js
- [ ] Tested Google Sign-In ✅
- [ ] Set Spotify env variables
- [ ] Started backend API
- [ ] Tested Spotify search ✅
- [ ] Read INTEGRATION_COMPLETE.md ✅

---

## 🎵 Ready to Go!

**All three auth methods are integrated and ready:**
1. ✅ Email/Password - Works now
2. ✅ Google OAuth - Needs Client ID (5 min setup)
3. ✅ Spotify - Needs credentials (5 min setup)

**Start here:** http://localhost:9000

---

*Last updated: January 24, 2026*
*Status: All authentication systems operational* ✅
