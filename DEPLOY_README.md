# 🚀 Deploy StarCy Backend to Railway

## Quick Start (5 Minutes)

### 1. Run the deployment helper

```bash
cd backend
./deploy.sh
```

This will:
- Check all required files
- Encode your secret files (APNs key, Google credentials)
- Initialize Git repository
- Give you step-by-step instructions

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Name: `starcy-backend`
3. **Make it PRIVATE** (contains secret files)
4. Don't initialize with README
5. Click "Create repository"

### 3. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/starcy-backend.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose `starcy-backend`
6. Railway will auto-deploy! ✨

### 5. Add Environment Variables

In Railway dashboard, go to Variables tab and add:

```
APNS_KEY_ID=9KR3NSQZD4
APNS_TEAM_ID=68F8CZM2Q7
APNS_BUNDLE_ID=com.star.starcyyy
APNS_KEY_BASE64=<paste from deploy.sh output>
ENVIRONMENT=production
GOOGLE_CREDENTIALS_BASE64=<paste from deploy.sh output>
```

### 6. Get Your Production URL

Railway will give you a URL like:
```
https://starcy-backend-production.up.railway.app
```

### 7. Update iOS App

In `BackendPushService.swift`, change:

```swift
private let backendURL = "https://starcy-backend-production.up.railway.app"
```

### 8. Test It!

```bash
curl https://starcy-backend-production.up.railway.app/
```

Should return:
```json
{"status":"running","service":"StarCy Backend",...}
```

## That's It! 🎉

Your backend is now running 24/7 on Railway!

## Cost

- **Free**: $5 credit (lasts ~1 month)
- **After free credit**: ~$5-10/month

## Monitoring

View logs in Railway dashboard:
- Click on your project
- Go to "Deployments" tab
- Click on latest deployment
- View logs in real-time

## Troubleshooting

### Deployment fails

Check Railway logs for errors. Common issues:
- Missing environment variables
- Invalid base64-encoded secrets
- Python version mismatch

### Can't connect to backend

- Check if deployment is successful (green checkmark in Railway)
- Verify URL is correct (https, not http)
- Check environment variables are set

### Google OAuth fails

You'll need to complete OAuth once after deployment:
1. Check Railway logs for OAuth URL
2. Open URL in browser
3. Authorize the app
4. Backend will save token and work automatically

**Note**: For production, you may want to use a service account instead of OAuth for Google APIs.

## Next Steps

1. Test with your iPhone
2. Monitor for 24 hours
3. Ready for App Store! 🚀

## Alternative: Deploy to Render

If you prefer Render over Railway:

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +"
4. Select "Web Service"
5. Connect your `starcy-backend` repo
6. Render will auto-detect Python
7. Add environment variables
8. Deploy!

**Note**: Render's free tier spins down after 15 minutes of inactivity, so use the paid tier ($7/month) for production.
