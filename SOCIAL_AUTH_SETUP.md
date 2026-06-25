# Social Authentication Setup Guide

This guide walks you through setting up Google and Facebook OAuth for your Resume Analyzer AI login page.

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r Req.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

## Google OAuth Setup

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Enter project name: `Resume Analyzer AI`
4. Click "Create"

### 2. Enable Google+ API
1. In the left sidebar, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

### 3. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen first:
   - Choose "External" user type
   - Fill in application name, user support email, developer contact
   - Click "Save and Continue"
   - Under "Scopes", add: `email`, `profile`, `openid`
   - Click "Save and Continue"
   - Add test users if needed
   - Review and click "Back to Dashboard"

4. Now create OAuth 2.0 Client ID:
   - Application type: "Web application"
   - Name: `Resume Analyzer AI`
   - Authorized JavaScript origins:
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
   - Authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - Click "Create"

5. Copy the **Client ID** and **Client Secret**

### 4. Add Google OAuth to Django

Go to Django Admin: `http://localhost:8000/admin/`

1. Navigate to "Sites" and set your site domain to `localhost:8000` (or your production domain)
2. Go to "Social applications" → "Add Social Application"
3. Fill in:
   - Provider: `Google`
   - Name: `Google OAuth`
   - Client id: [Paste Client ID from step 5]
   - Secret key: [Paste Client Secret from step 5]
   - Sites: Select `localhost:8000`
4. Click "Save"

**Alternatively, set environment variables:**
```bash
set GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
set GOOGLE_OAUTH_SECRET=your_client_secret_here
```

## Facebook OAuth Setup

### 1. Create a Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Choose "Consumer" as app type
4. Fill in:
   - App Name: `Resume Analyzer AI`
   - App Purpose: `Analyze resumes and conduct interviews`
5. Click "Create App"

### 2. Configure Facebook Login
1. In your app dashboard, click "Add Product"
2. Find "Facebook Login" and click "Set Up"
3. Choose "Web" as platform
4. Go to "Facebook Login" → "Settings"
5. Add Valid OAuth Redirect URIs:
   - `http://localhost:8000/accounts/facebook/login/callback/`
   - `http://127.0.0.1:8000/accounts/facebook/login/callback/`
6. Click "Save Changes"

### 3. Get Your App ID and Secret
1. In your app dashboard, go to "Settings" → "Basic"
2. Copy your **App ID** and **App Secret**

### 4. Add Facebook OAuth to Django

Go to Django Admin: `http://localhost:8000/admin/`

1. Go to "Social applications" → "Add Social Application"
2. Fill in:
   - Provider: `Facebook`
   - Name: `Facebook OAuth`
   - Client id: [Paste App ID from step 3]
   - Secret key: [Paste App Secret from step 3]
   - Sites: Select `localhost:8000`
3. Click "Save"

**Alternatively, set environment variables:**
```bash
set FACEBOOK_APP_ID=your_app_id_here
set FACEBOOK_APP_SECRET=your_app_secret_here
```

## Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Navigate to login page: `http://localhost:8000/login/`

3. You should now see:
   - Google login button ✅
   - Facebook login button ✅
   - Email login form ✅

## Troubleshooting

### "Redirect URI mismatch" error
- Make sure the redirect URIs in your provider settings exactly match the ones in Django
- Check that you're accessing the app from the correct domain/port

### "Social account does not exist" error
- This usually happens on first login - the user account gets created automatically
- If it persists, check that `SOCIALACCOUNT_AUTO_SIGNUP = True` in settings.py

### Provider buttons not appearing
- Make sure you ran migrations: `python manage.py migrate`
- Verify the social applications are configured in Django Admin
- Clear browser cache and refresh

## Production Setup

For production deployment:

1. Update `ALLOWED_HOSTS` in settings.py with your domain
2. Set `DEBUG = False` in settings.py
3. Use a secure SECRET_KEY (not the one shown in development)
4. Update OAuth redirect URIs in provider settings to use your production domain
5. Set environment variables for Client IDs and Secrets:
   ```bash
   export GOOGLE_OAUTH_CLIENT_ID=production_google_id
   export GOOGLE_OAUTH_SECRET=production_google_secret
   export FACEBOOK_APP_ID=production_facebook_id
   export FACEBOOK_APP_SECRET=production_facebook_secret
   ```

