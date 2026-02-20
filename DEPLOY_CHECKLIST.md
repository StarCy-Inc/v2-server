# ✅ Deployment Checklist - v2-server to Render

## Before You Start

**What you need:**
- [ ] GitHub username for v2-server repository
- [ ] Apple Developer Team ID
- [ ] APNs key file (`AuthKey_9KR3NSQZD4.p8`)

---

## Step 1: Get APNs Credentials

### Get Base64 Key:
```bash
cd StarCy-iOS/backend
base64 -i AuthKey_9KR3NSQZD4.p8 | pbcopy
```
- [ ] ✅ Base64 key copied to clipboard (save it!)

### Get Team ID:
1. Go to https://developer.apple.com/account
2. Click "Membership" → Copy Team ID
- [ ] ✅ Team ID saved (looks like `ABC123DEFG`)

---

## Step 2: Push to GitHub v2-server

### Automatic (Recommended):
```bash
cd StarCy-iOS/backend
./push_to_v2_server.sh
```
- [ ] ✅ Script completed successfully
- [ ] ✅ Repository visible at https://github.com/[username]/v2-server

### Manual (if script fails):
```bash
cd StarCy-iOS/backend
git init
git add .
git commit -m "Fixed backend for deployment"
git remote add origin https://github.com/[username]/v2-server.git
git push -u origin main
```
- [ ] ✅ Push completed without errors

---

## Step 3: Deploy to Render

### Create Web Service:
1. Go to https://render.com
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"
4. Connect to your **v2-server** repository

- [ ] ✅ Repository connected to Render

### Configure Settings:
- **Name:** `starcy-backend`
- **Root Directory:** (leave empty)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free

- [ ] ✅ Settings configured

### Add Environment Variables:
Click "Advanced" → Add these 5 variables:

1. `APNS_KEY_ID` = `9KR3NSQZD4`
2. `APNS_TEAM_ID` = `[your_team_id]`
3. `APNS_BUNDLE_ID` = `com.star.starcyyy`
4. `APNS_KEY_BASE64` = `[your_base64_key]`
5. `ENVIRONMENT` = `production`

- [ ] ✅ All 5 environment variables added

### Deploy:
- Click "Create Web Service"
- Wait 3-5 minutes for deployment

- [ ] ✅ Deployment successful (green status)
- [ ] ✅ Backend URL noted: `https://[service-name].onrender.com`

---

## Step 4: Test Deployment

### Run Test Script:
```bash
python StarCy-iOS/backend/test_deployment.py https://[your-url].onrender.com
```

**Expected results:**
- [ ] ✅ Health check passed
- [ ] ✅ Root endpoint working
- [ ] ✅ Device registration working
- [ ] ✅ All tests passed

### Quick Manual Test:
```bash
curl https://[your-url].onrender.com/health
```
Should return JSON with `"status": "healthy"`

- [ ] ✅ Manual health check passed

---

## Step 5: Update iOS App

### Update Backend URL:
1. Open `StarCy-iOS/starcy/Core/Services/BackendPushService.swift`
2. Find: `private let backendURL = "http://192.0.0.2:8000"`
3. Replace with: `private let backendURL = "https://[your-url].onrender.com"`

- [ ] ✅ iOS app updated with new URL

---

## Step 6: Test End-to-End

### Full Test:
1. Build and run iOS app
2. Check logs for "✅ Registered with backend"
3. Kill app completely
4. Add calendar event
5. Wait 2 minutes
6. Check Dynamic Island

- [ ] ✅ iOS app connects to backend
- [ ] ✅ Dynamic Island updates when app is killed
- [ ] ✅ Real-time monitoring working

---

## Troubleshooting

### If GitHub push fails:
- [ ] Check repository exists: https://github.com/[username]/v2-server
- [ ] Try: `git push --force origin main`
- [ ] Verify GitHub credentials

### If Render deployment fails:
- [ ] Check build logs in Render dashboard
- [ ] Verify all 5 environment variables are set
- [ ] Check repository has all files (main.py, requirements.txt, etc.)

### If iOS app can't connect:
- [ ] Verify URL is HTTPS (not HTTP)
- [ ] Test health endpoint manually
- [ ] Rebuild iOS app after URL change

---

## Success! 🎉

When everything is working:
- ✅ Backend runs 24/7 on Render
- ✅ Dynamic Island updates even when app is killed
- ✅ Real-time monitoring every 2 minutes
- ✅ Free tier covers 24/7 operation

**Your backend URL:** `https://[service-name].onrender.com`

---

## Quick Commands

```bash
# Get APNs key
base64 -i AuthKey_9KR3NSQZD4.p8 | pbcopy

# Push to GitHub
./push_to_v2_server.sh

# Test deployment
python test_deployment.py https://your-url.onrender.com
```

**Follow this checklist step by step and your deployment will work perfectly!** ✅