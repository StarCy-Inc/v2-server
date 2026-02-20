# Deploy to Render - Step by Step

## ✅ FIXES APPLIED
- Fixed circular import in `google_service.py` (removed duplicate instance declaration)
- Added missing `google_data_cache` variable in `main.py`
- Backend is now ready to deploy!

## 📋 Prerequisites
- GitHub account
- Render account (free tier available at https://render.com)
- Backend code in separate repo: `StarCy-Inc/v2-server`

## 🚀 Deployment Steps

### Step 1: Push Fixed Code to GitHub

```bash
# Navigate to backend folder
cd ~/Documents/StarCy/starcy-OS/StarCy-iOS/backend

# Add and commit fixes
git add google_service.py main.py
git commit -m "Fix: Resolve circular import and add google_data_cache"

# Push to your v2-server repo (you need to set this up)
# If you haven't set up the separate repo yet, do this:
git remote add v2-server https://github.com/StarCy-Inc/v2-server.git
git push v2-server star-yutish:main
```

### Step 2: Create Render Web Service

1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub account if not already connected
4. Select repository: `StarCy-Inc/v2-server`
5. Configure the service:
   - **Name**: `starcy-backend`
   - **Region**: Choose closest to you (e.g., Oregon, Ohio)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `.` if backend is in root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`

### Step 3: Add Environment Variables

In Render dashboard, go to "Environment" tab and add these variables:

```
APNS_KEY_ID=9KR3NSQZD4
APNS_TEAM_ID=68F8CZM2Q7
APNS_BUNDLE_ID=com.star.starcyyy
ENVIRONMENT=production
PORT=10000
```

For `APNS_KEY_BASE64`, run this command in your terminal:

```bash
cd ~/Documents/StarCy/starcy-OS/StarCy-iOS/backend
base64 -i AuthKey_9KR3NSQZD4.p8 | pbcopy
```

Then in Render, add:
```
APNS_KEY_BASE64=<paste the value from clipboard>
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Start the server
3. Wait for deployment to complete (2-3 minutes)
4. Your backend URL will be: `https://starcy-backend.onrender.com`

### Step 5: Test Deployment

```bash
# Test health endpoint
curl https://starcy-backend.onrender.com/health

# Expected response:
# {"status":"healthy","version":"3.0.0","active_devices":0,"monitoring_users":0}
```

### Step 6: Update iOS App

Update the backend URL in your iOS app:

File: `StarCy-iOS/starcy/Core/Services/BackendPushService.swift`

Change line 20 from:
```swift
private let baseURL = "http://localhost:8000"
```

To:
```swift
private let baseURL = "https://starcy-backend.onrender.com"
```

Then rebuild your iOS app in Xcode.

## 🎯 What Happens Next

1. Backend monitors Google Calendar/Gmail every 2 minutes
2. When changes detected, sends push notifications to iOS
3. Dynamic Island updates even when app is killed
4. Keep-alive notifications every 30 minutes to maintain Live Activity

## 🔍 Monitoring

- View logs in Render dashboard: https://dashboard.render.com
- Check active devices: `curl https://starcy-backend.onrender.com/devices`
- Health check: `curl https://starcy-backend.onrender.com/health`

## ⚠️ Important Notes

- **Free tier limitations**: 
  - Service spins down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds
  - 750 hours/month free (enough for 24/7 if only one service)
  
- **To keep service always running**: Upgrade to paid tier ($7/month) or use a cron job to ping the health endpoint every 10 minutes

## 🐛 Troubleshooting

### Deployment fails with import error
- Check that `google_service.py` and `main.py` have the latest fixes
- Verify `requirements.txt` includes all dependencies

### Push notifications not working
- Verify all environment variables are set correctly in Render
- Check that `APNS_KEY_BASE64` is properly encoded
- Ensure iOS app is using the correct Render URL

### Service keeps spinning down
- Free tier spins down after inactivity
- Upgrade to paid tier or set up a keep-alive ping service

## 📞 Support

If you encounter issues:
1. Check Render logs in dashboard
2. Test health endpoint
3. Verify environment variables
4. Check iOS app backend URL configuration
