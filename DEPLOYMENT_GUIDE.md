# Backend Deployment Guide - Railway

## Quick Deploy (5 Minutes)

### **Step 1: Create Railway Account**
1. Go to https://railway.app
2. Sign up with GitHub (free)
3. Verify your email

### **Step 2: Deploy Backend**

#### **Option A: Deploy from GitHub (Recommended)**
1. Push your code to GitHub
2. Go to Railway dashboard
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Select `StarCy-iOS/backend` as root directory
7. Railway auto-detects Python and deploys

#### **Option B: Deploy with Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to backend folder
cd StarCy-iOS/backend

# Initialize and deploy
railway init
railway up
```

### **Step 3: Configure Environment Variables**

In Railway dashboard, add these variables:

```
APNS_KEY_ID=your_key_id
APNS_TEAM_ID=your_team_id
APNS_BUNDLE_ID=com.star.starcyyy
APNS_KEY_BASE64=<base64_encoded_p8_key>
ENVIRONMENT=production
PORT=8000
```

**To get APNS_KEY_BASE64:**
```bash
cd StarCy-iOS/backend
base64 -i AuthKey_9KR3NSQZD4.p8
# Copy the output
```

### **Step 4: Get Your Backend URL**

Railway will give you a URL like:
```
https://your-app-name.up.railway.app
```

Copy this URL - you'll need it for iOS app.

### **Step 5: Update iOS App**

Update `BackendPushService.swift`:

```swift
// Change this line:
private let backendURL = "http://192.0.0.2:8000"

// To your Railway URL:
private let backendURL = "https://your-app-name.up.railway.app"
```

### **Step 6: Test Deployment**

```bash
# Test health endpoint
curl https://your-app-name.up.railway.app/health

# Should return:
{"status": "healthy", "version": "3.0.0"}
```

## Alternative: Deploy to Render

### **Step 1: Create Render Account**
1. Go to https://render.com
2. Sign up with GitHub (free)

### **Step 2: Create Web Service**
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name:** starcy-backend
   - **Root Directory:** StarCy-iOS/backend
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **Step 3: Add Environment Variables**
Same as Railway (see above)

### **Step 4: Deploy**
Click "Create Web Service" - Render will deploy automatically

## Alternative: Deploy to Heroku

### **Step 1: Install Heroku CLI**
```bash
brew install heroku/brew/heroku
```

### **Step 2: Login and Create App**
```bash
heroku login
cd StarCy-iOS/backend
heroku create starcy-backend
```

### **Step 3: Set Environment Variables**
```bash
heroku config:set APNS_KEY_ID=your_key_id
heroku config:set APNS_TEAM_ID=your_team_id
heroku config:set APNS_BUNDLE_ID=com.star.starcyyy
heroku config:set APNS_KEY_BASE64=<base64_key>
heroku config:set ENVIRONMENT=production
```

### **Step 4: Deploy**
```bash
git add .
git commit -m "Deploy backend"
git push heroku main
```

## Troubleshooting

### **Backend Not Starting**
Check logs:
```bash
# Railway
railway logs

# Render
# View logs in dashboard

# Heroku
heroku logs --tail
```

### **APNs Not Working**
1. Verify APNS_KEY_BASE64 is correct
2. Check APNS_TEAM_ID matches Apple Developer account
3. Ensure APNS_KEY_ID matches your .p8 file

### **iOS App Can't Connect**
1. Verify backend URL is HTTPS (not HTTP)
2. Check backend is running: `curl https://your-url/health`
3. Look for errors in iOS logs

## Cost

All three platforms offer free tiers:
- **Railway:** 500 hours/month free
- **Render:** 750 hours/month free
- **Heroku:** 1000 hours/month free (with credit card)

## Next Steps

After deployment:
1. Update iOS app with new backend URL
2. Rebuild and test iOS app
3. Add calendar event while app is killed
4. Dynamic Island should update within 2 minutes!

## Monitoring

Check backend is working:
```bash
# Health check
curl https://your-url/health

# Check active devices
curl https://your-url/devices

# View logs
railway logs  # or render/heroku equivalent
```