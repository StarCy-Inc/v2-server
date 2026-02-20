# 🚀 Quick Start: Deploy to Render

## ✅ What I Fixed
1. **Circular import error** in `google_service.py` - The file was trying to import itself
2. **Missing variable** `google_data_cache` in `main.py` - Added initialization
3. **Created deployment guides** - Step-by-step instructions below

## 🎯 Your Next Steps (Copy & Paste These Commands)

### Step 1: Push Backend to Separate Repo

Open your terminal and run these commands:

```bash
# Navigate to backend folder
cd ~/Documents/StarCy/starcy-OS/StarCy-iOS/backend

# Run the push script
./push_to_render.sh
```

This will push your backend code to the `StarCy-Inc/v2-server` repository.

### Step 2: Get Your APNs Key (Base64)

```bash
# Copy the base64-encoded APNs key to clipboard
base64 -i AuthKey_9KR3NSQZD4.p8 | pbcopy
```

The key is now in your clipboard. You'll paste it in Render in Step 4.

### Step 3: Create Render Service

1. Open https://render.com/dashboard in your browser
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if needed
4. Select repository: **StarCy-Inc/v2-server**
5. Click **"Connect"**

### Step 4: Configure Service

Fill in these settings:

- **Name**: `starcy-backend`
- **Region**: `Oregon (US West)` (or closest to you)
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Instance Type**: `Free`

### Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Key | Value |
|-----|-------|
| `APNS_KEY_ID` | `9KR3NSQZD4` |
| `APNS_TEAM_ID` | `68F8CZM2Q7` |
| `APNS_BUNDLE_ID` | `com.star.starcyyy` |
| `ENVIRONMENT` | `production` |
| `PORT` | `10000` |
| `APNS_KEY_BASE64` | (Paste from clipboard - Step 2) |

### Step 6: Deploy!

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Your backend URL will be: `https://starcy-backend.onrender.com`

### Step 7: Test It

Run this in your terminal:

```bash
curl https://starcy-backend.onrender.com/health
```

Expected response:
```json
{"status":"healthy","version":"3.0.0","active_devices":0,"monitoring_users":0}
```

### Step 8: Update iOS App

Open Xcode and update the backend URL:

**File**: `StarCy-iOS/starcy/Core/Services/BackendPushService.swift`

**Line 20**, change from:
```swift
private let baseURL = "http://localhost:8000"
```

To:
```swift
private let baseURL = "https://starcy-backend.onrender.com"
```

Then **rebuild** your iOS app.

## 🎉 Done!

Your backend is now deployed and will:
- ✅ Monitor Google Calendar/Gmail every 2 minutes
- ✅ Send push notifications when changes detected
- ✅ Update Dynamic Island even when app is killed
- ✅ Keep Live Activity alive with periodic updates

## 📊 Monitor Your Backend

- **Logs**: https://dashboard.render.com → Select your service → Logs tab
- **Check devices**: `curl https://starcy-backend.onrender.com/devices`
- **Health check**: `curl https://starcy-backend.onrender.com/health`

## ⚠️ Free Tier Note

Render's free tier spins down after 15 minutes of inactivity. The first request after spin-down takes 30-60 seconds to wake up. For 24/7 uptime, upgrade to the paid tier ($7/month).

## 🐛 Troubleshooting

**Deployment fails?**
- Check Render logs in dashboard
- Verify all environment variables are set
- Make sure `APNS_KEY_BASE64` was pasted correctly

**Push notifications not working?**
- Test health endpoint first
- Verify iOS app is using correct Render URL
- Check Render logs for errors

**Need help?**
- Full guide: `RENDER_DEPLOY.md`
- Check Render documentation: https://render.com/docs
