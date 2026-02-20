# Your Personal Setup Checklist

I can see you already have an APNs key! Let's get this running in 5 minutes.

## ✅ What You Already Have

From your screenshot, I can see:
- **Key ID**: `9KR3NSQZD4` ✅
- **Team ID**: `68F8CZM2Q7` ✅
- **Key Name**: "StarCy Push"

You just need to download the `.p8` file if you haven't already!

---

## 🚀 Quick Setup (5 Minutes)

### 1. Download Your Key (if you haven't)

Go to: https://developer.apple.com/account/resources/authkeys/list

Find "StarCy Push" and click **Download** (you can only do this once!)

The file will be named: `AuthKey_9KR3NSQZD4.p8`

---

### 2. Open Terminal

Press `Cmd + Space`, type `Terminal`, press Enter

---

### 3. Go to Backend Folder

```bash
cd ~/Documents/StarCy/starcy-os/backend
```

---

### 4. Run Setup

```bash
./setup.sh
```

Wait for it to finish (installs Python packages)

---

### 5. Copy Your Key File

```bash
cp ~/Downloads/AuthKey_9KR3NSQZD4.p8 ./
```

---

### 6. Create Config File

```bash
cp .env.example .env
open -a TextEdit .env
```

**Edit the file to look like this:**

```env
APNS_KEY_ID=9KR3NSQZD4
APNS_TEAM_ID=68F8CZM2Q7
APNS_BUNDLE_ID=com.yutish.starcy
APNS_KEY_PATH=./AuthKey_9KR3NSQZD4.p8
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
```

**Replace `com.yutish.starcy` with your actual Bundle ID:**
- Open Xcode
- Click your project (blue icon)
- Click "starcy" under TARGETS
- Copy the "Bundle Identifier"

**Save and close TextEdit**

---

### 7. Start Server

```bash
source venv/bin/activate
python main.py
```

You should see:
```
✅ Scheduler started - Dynamic Island will rotate every 20 seconds
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this Terminal window open!**

---

### 8. Get Your Mac's IP

Open a **NEW** Terminal window (Cmd + N):

```bash
ipconfig getifaddr en0
```

You'll see something like: `192.168.1.100`

**Write this down!**

---

### 9. Update iOS App

In Xcode, open: `starcy/Core/Services/BackendPushService.swift`

Find line 20 and change it to:

```swift
private let backendURL = "http://192.168.1.100:8000"
```

(Use YOUR IP address from step 8)

**Save the file** (Cmd + S)

---

### 10. Test on iPhone

1. **Connect your iPhone** to your Mac
2. **Select your iPhone** in Xcode (top left dropdown)
3. **Click Play** (▶️) to run the app
4. **Watch Xcode console** for:
   ```
   📱 Device token received
   ✅ Registered with backend
   ```
5. **Watch Terminal** for:
   ```
   📱 Device registered
   🔄 Running periodic rotation
   ✅ Live Activity updated
   ```
6. **Close the app completely** on your iPhone
7. **Watch the Dynamic Island** - it should keep rotating every 20 seconds!

---

## 🎉 Done!

Your Dynamic Island is now active 24/7!

---

## 🐛 If Something Goes Wrong

### Can't find the .p8 file?

Check your Downloads folder:
```bash
ls ~/Downloads/AuthKey*
```

If it's not there, you need to download it from Apple Developer Portal.

### Server won't start?

Make sure you're in the right folder:
```bash
pwd
```

Should show: `/Users/staryutish/Documents/StarCy/starcy-os/backend`

### iPhone not connecting?

1. Make sure iPhone and Mac are on the **same WiFi**
2. Check the IP address is correct
3. Test in Safari: go to `http://192.168.1.100:8000` (use your IP)

### Still stuck?

Open `backend/STEP_BY_STEP_GUIDE.md` for detailed troubleshooting!

---

## 📝 Your Info (for reference)

- **Key ID**: `9KR3NSQZD4`
- **Team ID**: `68F8CZM2Q7`
- **Key File**: `AuthKey_9KR3NSQZD4.p8`
- **Bundle ID**: (get from Xcode)
- **Mac IP**: (get from step 8)

---

**Ready? Start with step 1!** 🚀
