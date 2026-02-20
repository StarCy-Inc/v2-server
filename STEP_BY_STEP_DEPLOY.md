# 🚀 Step-by-Step Deployment Guide

## Overview
We'll deploy the **fixed backend** to your **v2-server** GitHub repository, then connect it to Render.

## Prerequisites
- ✅ GitHub account with access to **v2-server** repository
- ✅ Render account (free tier is fine)
- ✅ Apple Developer account for APNs credentials

---

## Step 1: Prepare APNs Credentials (2 minutes)

### Get your APNs Key in Base64 format:
```bash
cd StarCy-iOS/backend
base64 -i AuthKey_9KR3NSQZD4.p8 | pbcopy
```
**✅ Your base64 key is now copied to clipboard - save it somewhere!**

### Get your Team ID:
1. Go to https://developer.apple.com/account
2. Click "Membership" in sidebar
3. Copy your **Team ID** (10 characters like `ABC123DEFG`)

---

## Step 2: Push Backend to v2-server Repository (3 minutes)

### Option A: If v2-server repo is empty/new
```bash
# Navigate to backend directory
cd StarCy-iOS/backend

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit with message
git commit -m "Fixed backend deployment - ready for Render"

# Add your v2-server repository as remote
git remote add origin https://github.com/[your-username]/v2-server.git

# Push to main branch
git push -u origin main
```

### Option B: If v2-server repo already exists
```bash
# Clone your v2-server repository
git clone https://github.com/[your-username]/v2-server.git
cd v2-server

# Copy all backend files to the repository
cp -r ../StarCy-iOS/backend/* .

# Add and commit
git add .
git commit -m "Updated backend with deployment fixes"

# Push to GitHub
git push origin main
```

**✅ Your fixed backend is now on GitHub in v2-server repository**

---

## Step 3: Deploy to Render (5 minutes)

### A. Create Render Account
1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with GitHub
4. Authorize Render to access your repositories

### B. Create Web Service
1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Find and select your **v2-server** repository
5. Click **"Connect"**

### C. Configure Deployment Settings
Fill in these settings:

**Basic Settings:**
- **Name:** `starcy-backend` (or any name you prefer)
- **Region:** `Oregon (US West)` (or closest to you)
- **Branch:** `main`
- **Root Directory:** Leave **EMPTY** (since backend files are in root)
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Pricing:**
- Select **"Free"** plan

### D. Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these **5 variables**:

1. **APNS_KEY_ID**
   - Value: `9KR3NSQZD4`

2. **APNS_TEAM_ID**
   - Value: `[your_team_id_from_step_1]`

3. **APNS_BUNDLE_ID**
   - Value: `com.star.starcyyy`

4. **APNS_KEY_BASE64**
   - Value: `[paste_the_base64_key_from_step_1]`

5. **ENVIRONMENT**
   - Value: `production`

### E. Deploy!
1. Click **"Create Web Service"**
2. Wait for deployment (3-5 minutes)
3. Watch the build logs - should see:
   ```
   ✅ Backend server starting...
   ✅ Scheduler started
   ```

**✅ Your backend URL will be:** `https://starcy-backend.onrender.com`

---

## Step 4: Test Your Deployment (2 minutes)

### Test the backend:
```bash
# Replace with your actual Render URL
python StarCy-iOS/backend/test_deployment.py https://starcy-backend.onrender.com
```

**Expected output:**
```
✅ Health check passed
✅ Root endpoint working
✅ Device registration working
✅ All tests passed! Your backend is ready.
```

### Quick manual test:
```bash
curl https://starcy-backend.onrender.com/health
```

**Should return:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "active_devices": 0,
  "monitoring_users": 0
}
```

---

## Step 5: Update iOS App (1 minute)

### Find and update the backend URL:
1. Open `StarCy-iOS/starcy/Core/Services/BackendPushService.swift`
2. Find this line:
   ```swift
   private let backendURL = "http://192.0.0.2:8000"
   ```
3. Replace with your Render URL:
   ```swift
   private let backendURL = "https://starcy-backend.onrender.com"
   ```
4. Save the file

---

## Step 6: Test End-to-End (3 minutes)

### Test the complete flow:
1. **Build and run** your iOS app
2. **Check Xcode logs** for:
   ```
   ✅ Registered with backend for real-time monitoring
   🔍 Real-time monitoring ENABLED
   ```
3. **Kill the app completely** (swipe up and remove from app switcher)
4. **Add a calendar event** on your phone
5. **Wait 2 minutes**
6. **Check Dynamic Island** - should show the new event!

---

## Troubleshooting

### If GitHub push fails:
```bash
# Make sure you're in the right directory
pwd  # Should show path ending in /backend

# Check git status
git status

# If remote already exists, remove and re-add
git remote remove origin
git remote add origin https://github.com/[your-username]/v2-server.git
git push -u origin main
```

### If Render deployment fails:
1. Check **"Logs"** tab in Render dashboard
2. Look for specific error messages
3. Verify all 5 environment variables are set correctly
4. Make sure repository has all the fixed files

### If iOS app can't connect:
1. Verify backend URL is **HTTPS** (not HTTP)
2. Test health endpoint manually
3. Check iOS logs for connection errors
4. Rebuild and reinstall iOS app

---

## Success Checklist

- [ ] ✅ APNs credentials prepared (base64 key + team ID)
- [ ] ✅ Backend pushed to v2-server GitHub repository
- [ ] ✅ Render web service created and deployed
- [ ] ✅ All 5 environment variables added to Render
- [ ] ✅ Test script passes all checks
- [ ] ✅ iOS app updated with new backend URL
- [ ] ✅ End-to-end test: app killed → calendar event → Dynamic Island updates

---

## What Happens Next

🎉 **Your Dynamic Island now works 24/7!**

- Backend monitors your calendar/email every 2 minutes
- Sends push notifications when changes detected
- Updates Dynamic Island even when app is completely killed
- Runs on Render's free tier (500 hours/month = 24/7 coverage)

**Your backend URL:** `https://starcy-backend.onrender.com`

---

## Quick Commands Summary

```bash
# 1. Get APNs key
cd StarCy-iOS/backend && base64 -i AuthKey_9KR3NSQZD4.p8 | pbcopy

# 2. Push to GitHub (if new repo)
git init && git add . && git commit -m "Fixed backend" && git remote add origin https://github.com/[username]/v2-server.git && git push -u origin main

# 3. Test deployment
python StarCy-iOS/backend/test_deployment.py https://your-url.onrender.com
```

**Ready to deploy! Follow the steps above and your Dynamic Island will work perfectly.** 🚀