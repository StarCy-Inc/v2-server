# Quick Start Guide - 5 Minutes to 24/7 Dynamic Island

## Step 1: Get APNs Credentials (2 minutes)

1. Go to https://developer.apple.com/account/resources/authkeys/list
2. Click **+** button
3. Name: "StarCy Push"
4. Check: **Apple Push Notifications service (APNs)**
5. Click **Continue** → **Register** → **Download**
6. Save the `.p8` file
7. Note your **Key ID** (e.g., `ABC123XYZ`)
8. Note your **Team ID** (top right, e.g., `TEAM123456`)

## Step 2: Setup Backend (2 minutes)

```bash
cd backend

# Run setup script
./setup.sh

# Copy your .p8 file here
cp ~/Downloads/AuthKey_*.p8 ./

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials
```

In `.env`, update:
```env
APNS_KEY_ID=ABC123XYZ
APNS_TEAM_ID=TEAM123456
APNS_BUNDLE_ID=com.yourcompany.starcy
APNS_KEY_PATH=./AuthKey_ABC123XYZ.p8
```

## Step 3: Start Server (30 seconds)

```bash
source venv/bin/activate
python main.py
```

You should see:
```
✅ Scheduler started - Dynamic Island will rotate every 20 seconds
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Update iOS App (30 seconds)

Find your Mac's IP address:
```bash
ipconfig getifaddr en0
# Example output: 192.168.1.100
```

Open `starcy/Core/Services/BackendPushService.swift` and update:
```swift
private let backendURL = "http://192.168.1.100:8000"
```

## Step 5: Test (1 minute)

1. Build and run iOS app on **real device** (not simulator)
2. Check Xcode console:
   ```
   📱 Device token received: 1234abcd...
   ✅ Registered with backend
   ```
3. Check backend terminal:
   ```
   📱 Device registered: 1234abcd...
   🔄 Running periodic rotation at 12:34:56
   ✅ Live Activity updated for device 1234abcd...
   ```
4. **Close the app completely** (swipe up from app switcher)
5. Watch Dynamic Island continue rotating! 🎉

## Troubleshooting

### "Device token not received"
- Must use **real device** (not simulator)
- Check push permissions are granted
- Restart app

### "Backend registration failed"
- Check backend is running: `curl http://192.168.1.100:8000/`
- Verify IP address is correct
- Check device and Mac are on same WiFi

### "Push notifications not working"
- Verify `.env` credentials are correct
- Check `.p8` file path is correct
- Use `ENVIRONMENT=development` for debug builds
- Check backend logs for errors

## Next Steps

- **Production**: Deploy to VPS or cloud platform (see `SETUP_GUIDE.md`)
- **Customize**: Edit rotation logic in `main.py`
- **Monitor**: Check `/devices` endpoint for registered devices
- **Scale**: Add more content types and smarter rotation

## Test Backend

```bash
python test_backend.py
```

This will verify:
- ✅ APNs configuration
- ✅ API endpoints
- ✅ Device registration
- ✅ Server health

## Production Checklist

- [ ] Deploy backend to VPS/cloud
- [ ] Update `backendURL` to production URL
- [ ] Change `ENVIRONMENT=production` in `.env`
- [ ] Setup HTTPS (nginx reverse proxy)
- [ ] Add API authentication
- [ ] Setup monitoring/logging
- [ ] Configure systemd service for auto-restart

## Support

- Full setup guide: `SETUP_GUIDE.md`
- Architecture docs: `../DYNAMIC_ISLAND_24_7_SOLUTION.md`
- API reference: `README.md`

---

**That's it!** Your Dynamic Island now rotates 24/7, even when the app is closed. 🚀
