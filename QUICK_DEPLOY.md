# Quick Deploy - 5 Minutes ⚡

## Option 1: Railway (Easiest - Recommended)

### **1. Create Account**
Go to https://railway.app and sign up with GitHub

### **2. Deploy**
```bash
cd StarCy-iOS/backend
./deploy_railway.sh
```

### **3. Add Environment Variables**
In Railway dashboard, add:
- `APNS_KEY_ID` = `9KR3NSQZD4`
- `APNS_TEAM_ID` = Your Apple Team ID
- `APNS_BUNDLE_ID` = `com.star.starcyyy`
- `APNS_KEY_BASE64` = Run: `base64 -i AuthKey_9KR3NSQZD4.p8`
- `ENVIRONMENT` = `production`

### **4. Get Your URL**
Railway will show your URL like: `https://starcy-backend-production.up.railway.app`

### **5. Update iOS App**
Edit `StarCy-iOS/starcy/Core/Services/BackendPushService.swift`:
```swift
private let backendURL = "https://your-railway-url.up.railway.app"
```

### **6. Test**
```bash
curl https://your-railway-url.up.railway.app/health
```

Should return:
```json
{"status": "healthy", "version": "3.0.0"}
```

## Option 2: One-Click Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click button above
2. Connect GitHub
3. Add environment variables (same as Railway)
4. Deploy!

## Option 3: Manual Deploy

### **Railway**
```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd StarCy-iOS/backend
railway init
railway up
```

### **Render**
1. Go to https://render.com
2. New > Web Service
3. Connect GitHub repo
4. Root Directory: `StarCy-iOS/backend`
5. Build: `pip install -r requirements.txt`
6. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **Heroku**
```bash
# Install CLI
brew install heroku/brew/heroku

# Login and deploy
heroku login
cd StarCy-iOS/backend
heroku create starcy-backend
git push heroku main
```

## Getting APNs Credentials

### **1. APNS_KEY_ID**
Look at your .p8 file name: `AuthKey_9KR3NSQZD4.p8`
The key ID is: `9KR3NSQZD4`

### **2. APNS_TEAM_ID**
1. Go to https://developer.apple.com/account
2. Click "Membership"
3. Copy "Team ID"

### **3. APNS_KEY_BASE64**
```bash
cd StarCy-iOS/backend
base64 -i AuthKey_9KR3NSQZD4.p8
```
Copy the entire output (it's long)

## Troubleshooting

### **"Module not found" error**
```bash
pip install -r requirements.txt
```

### **"Port already in use"**
Backend is already running locally. Kill it:
```bash
pkill -f uvicorn
```

### **iOS app can't connect**
1. Check backend URL is HTTPS (not HTTP)
2. Verify backend is running: `curl https://your-url/health`
3. Check iOS logs for connection errors

## What Happens After Deploy

1. Backend runs 24/7 on cloud
2. iOS app registers with backend
3. Backend monitors your calendar/email every 2 minutes
4. When changes detected, backend pushes update to Dynamic Island
5. Dynamic Island updates even when app is killed!

## Cost

All platforms have free tiers:
- Railway: 500 hours/month free
- Render: 750 hours/month free  
- Heroku: 1000 hours/month free

Your backend will use ~720 hours/month (24/7), so free tier is enough!

## Next Steps

After deployment:
1. ✅ Backend is running
2. ✅ Update iOS app with backend URL
3. ✅ Rebuild iOS app
4. ✅ Test: Kill app, add calendar event, wait 2 minutes
5. ✅ Dynamic Island updates automatically!

## Support

If you get stuck:
1. Check Railway/Render logs
2. Test health endpoint: `curl https://your-url/health`
3. Check iOS logs for connection errors