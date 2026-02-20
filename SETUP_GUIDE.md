# Backend Setup Guide

## Quick Start (5 minutes)

### 1. Get APNs Credentials

1. Go to [Apple Developer Portal](https://developer.apple.com/account/resources/authkeys/list)
2. Click the **+** button to create a new key
3. Name it "StarCy Push Notifications"
4. Check **Apple Push Notifications service (APNs)**
5. Click **Continue** → **Register**
6. **Download** the `.p8` file (you can only download it once!)
7. Note your **Key ID** (e.g., `ABC123XYZ`)
8. Note your **Team ID** (top right corner, e.g., `TEAM123456`)

### 2. Setup Backend

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Update these values:
```env
APNS_KEY_ID=ABC123XYZ          # Your Key ID from step 1
APNS_TEAM_ID=TEAM123456        # Your Team ID from step 1
APNS_BUNDLE_ID=com.yourcompany.starcy  # Your app's bundle ID
APNS_KEY_PATH=./AuthKey_ABC123XYZ.p8   # Path to your .p8 file
ENVIRONMENT=development        # Use 'production' for TestFlight/App Store
```

### 4. Copy APNs Key

```bash
# Copy your downloaded .p8 file to the backend folder
cp ~/Downloads/AuthKey_ABC123XYZ.p8 ./
```

### 5. Run Server

```bash
source venv/bin/activate
python main.py
```

You should see:
```
✅ Scheduler started - Dynamic Island will rotate every 20 seconds
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Update iOS App

Open `starcy/Core/Services/BackendPushService.swift` and update:

```swift
private let backendURL = "http://YOUR_SERVER_IP:8000"
```

Replace `YOUR_SERVER_IP` with:
- **Local testing**: `http://192.168.1.X:8000` (your Mac's local IP)
- **Production**: `https://your-domain.com` (your server URL)

### 7. Test It

1. Build and run the iOS app
2. Check Xcode console for:
   ```
   📱 Device token received: 1234abcd...
   ✅ Registered with backend
   ```
3. Check backend logs for:
   ```
   📱 Device registered: 1234abcd... (Activity: ...)
   🔄 Running periodic rotation at 12:34:56
   ✅ Live Activity updated for device 1234abcd...
   ```

## Production Deployment

### Option 1: VPS (DigitalOcean, AWS, etc.)

1. **Create a server** (Ubuntu 22.04 recommended)
2. **Install Python**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
3. **Upload backend files**:
   ```bash
   scp -r backend/ user@your-server:/opt/starcy-backend
   ```
4. **Setup systemd service**:
   ```bash
   sudo nano /etc/systemd/system/starcy-backend.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=StarCy Backend Server
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/starcy-backend
   Environment="PATH=/opt/starcy-backend/venv/bin"
   ExecStart=/opt/starcy-backend/venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start service**:
   ```bash
   sudo systemctl enable starcy-backend
   sudo systemctl start starcy-backend
   sudo systemctl status starcy-backend
   ```

### Option 2: Docker

```bash
cd backend
docker build -t starcy-backend .
docker run -d -p 8000:8000 --name starcy --restart always starcy-backend
```

### Option 3: Railway/Render/Fly.io

1. Create account on [Railway](https://railway.app) (easiest)
2. Click **New Project** → **Deploy from GitHub**
3. Select your repo
4. Add environment variables in dashboard
5. Deploy!

## Troubleshooting

### "Device token not received"
- Check push notification permissions are granted
- Verify app is running on a real device (not simulator)
- Check Xcode console for errors

### "Backend registration failed"
- Verify backend server is running
- Check `backendURL` in `BackendPushService.swift`
- Test backend: `curl http://YOUR_SERVER:8000/`

### "Live Activity not updating"
- Check APNs credentials are correct
- Verify `.p8` file path is correct
- Check `ENVIRONMENT` matches your build (development/production)
- View backend logs for errors

### "Push notifications not working"
- Development builds use sandbox APNs
- Production builds use production APNs
- TestFlight builds use production APNs
- Verify bundle ID matches exactly

## Finding Your Mac's Local IP

```bash
# macOS
ipconfig getifaddr en0

# Or check System Settings → Network
```

## Security Notes

- **Never commit** `.env` or `.p8` files to git
- Use HTTPS in production (setup nginx reverse proxy)
- Consider adding API authentication for production
- Rotate APNs keys periodically

## Cost Estimate

- **VPS**: $5-10/month (DigitalOcean, Linode)
- **Railway**: Free tier available, then $5/month
- **AWS**: ~$3-5/month (t2.micro)
- **APNs**: Free (unlimited push notifications)

## Support

If you run into issues:
1. Check backend logs: `tail -f /var/log/starcy-backend.log`
2. Check iOS logs in Xcode console
3. Test backend health: `curl http://YOUR_SERVER:8000/devices`
