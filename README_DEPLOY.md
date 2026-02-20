# 🚀 Deploy Your Backend - Start Here!

## Quick Start (5 Minutes)

### **Option 1: Automated Wizard (Easiest)**

```bash
cd StarCy-iOS/backend
./START_DEPLOYMENT.sh
```

The wizard will:
- ✅ Check prerequisites
- ✅ Get your APNs credentials
- ✅ Login to Railway
- ✅ Set environment variables
- ✅ Deploy your backend
- ✅ Give you next steps

### **Option 2: Manual Deployment**

Follow the detailed guide: **[DEPLOY_NOW.md](./DEPLOY_NOW.md)**

## What You Need

1. **Apple Developer Account**
   - APNs key file: `AuthKey_9KR3NSQZD4.p8` (already in this folder)
   - Team ID from https://developer.apple.com/account

2. **GitHub Account**
   - For Railway login

3. **5 Minutes**
   - That's it!

## After Deployment

1. Get your backend URL from Railway
2. Update `BackendPushService.swift` with the URL
3. Rebuild iOS app
4. Test: Kill app, add calendar event, wait 2 minutes
5. ✅ Dynamic Island updates automatically!

## Files in This Folder

- **START_DEPLOYMENT.sh** - Automated deployment wizard
- **DEPLOY_NOW.md** - Complete step-by-step guide
- **QUICK_DEPLOY.md** - Quick reference
- **DEPLOYMENT_GUIDE.md** - Detailed options
- **main.py** - Backend server code
- **requirements.txt** - Python dependencies
- **railway.toml** - Railway configuration
- **render.yaml** - Render configuration

## Support

If you get stuck:
1. Read [DEPLOY_NOW.md](./DEPLOY_NOW.md)
2. Check Railway logs: `railway logs`
3. Test health: `curl https://your-url/health`

## What This Backend Does

- 🔍 Monitors your Google Calendar/Gmail every 2 minutes
- 📱 Sends push notifications to update Dynamic Island
- ⚡ Works even when iOS app is completely killed
- 🔄 Updates within 2 minutes of any calendar/email change
- 🆓 Runs on free tier (Railway/Render)

---

**Ready to deploy? Run `./START_DEPLOYMENT.sh` now!** 🚀