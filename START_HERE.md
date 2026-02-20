# 👋 START HERE - Complete Beginner's Guide

## What You're Building

You're setting up a small server on your Mac that will keep your iPhone's Dynamic Island active 24/7 by sending it updates every 20 seconds.

**Think of it like this:**
- Your Mac = A radio station 📻
- Your iPhone = A radio receiver 📱
- Apple's servers = The airwaves 🌐

Your Mac broadcasts updates → Apple delivers them → Your iPhone receives them → Dynamic Island updates!

---

## 📋 What You Need

- ✅ Your Mac (the one you're using now)
- ✅ Your iPhone (must be a real device, not simulator)
- ✅ Both on the same WiFi network
- ✅ 15 minutes of time
- ✅ Your Apple Developer account

---

## 🎯 Three Simple Steps

### Step 1: Get Your Apple Credentials (5 min)
You need a special key from Apple to send push notifications.

**I can see you already created one!** 🎉
- Key ID: `9KR3NSQZD4`
- Team ID: `68F8CZM2Q7`

Just download the `.p8` file from Apple Developer Portal if you haven't.

### Step 2: Setup the Server (5 min)
Install Python packages and configure the server with your credentials.

### Step 3: Connect Your iPhone (5 min)
Update your iOS app to talk to the server and test it!

---

## 🚀 Let's Go!

### Choose Your Guide:

1. **Super Quick (for experienced developers)**
   → Open `YOUR_CHECKLIST.md`
   → 10 commands, done in 5 minutes

2. **Step-by-Step (first time doing this)**
   → Open `STEP_BY_STEP_GUIDE.md`
   → Every single step explained with screenshots

3. **Just the Commands (copy-paste)**
   → See below ⬇️

---

## ⚡ Copy-Paste Commands (Fastest Way)

Open Terminal and run these one by one:

```bash
# 1. Go to backend folder
cd ~/Documents/StarCy/starcy-os/backend

# 2. Run setup
./setup.sh

# 3. Copy your key file (replace XXXXXXXXXX with your actual filename)
cp ~/Downloads/AuthKey_9KR3NSQZD4.p8 ./

# 4. Create config
cp .env.example .env

# 5. Edit config (opens TextEdit)
open -a TextEdit .env
```

**In TextEdit, change these lines:**
```env
APNS_KEY_ID=9KR3NSQZD4
APNS_TEAM_ID=68F8CZM2Q7
APNS_BUNDLE_ID=YOUR_BUNDLE_ID_HERE
APNS_KEY_PATH=./AuthKey_9KR3NSQZD4.p8
```

**Save and close TextEdit**, then continue:

```bash
# 6. Start server
source venv/bin/activate
python main.py
```

**Open a NEW Terminal window** (Cmd + N):

```bash
# 7. Get your Mac's IP
ipconfig getifaddr en0
```

**Write down the IP address** (like `192.168.1.100`)

**In Xcode:**
1. Open `starcy/Core/Services/BackendPushService.swift`
2. Change line 20 to: `private let backendURL = "http://YOUR_IP:8000"`
3. Save (Cmd + S)
4. Run on your iPhone (▶️)

**Done!** 🎉

---

## 🎬 What Happens Next?

1. **Xcode Console** will show:
   ```
   📱 Device token received: abc123...
   ✅ Registered with backend
   ```

2. **Terminal** will show:
   ```
   📱 Device registered: abc123...
   🔄 Running periodic rotation at 12:34:56
   ✅ Live Activity updated for device abc123...
   ```

3. **Your iPhone** will show the Dynamic Island

4. **Close the app** completely (swipe up, swipe away)

5. **Watch the Dynamic Island** - it keeps rotating every 20 seconds!

---

## ❓ Common Questions

### Do I need to keep Terminal open?
**Yes**, for now. The server runs in Terminal. Later you can deploy to a cloud server.

### Does my Mac need to stay on?
**Yes**, for now. Or deploy to a cloud server ($5/month).

### What if I close the iPhone app?
**It keeps working!** That's the whole point - Dynamic Island stays active 24/7.

### Can I use the simulator?
**No**, push notifications only work on real devices.

### What if I'm not on WiFi?
Your iPhone needs internet. WiFi or cellular both work, but Mac and iPhone should be on same WiFi for local testing.

---

## 🆘 Need Help?

### Quick Fixes

**"Command not found"**
→ Make sure you're in the backend folder: `cd ~/Documents/StarCy/starcy-os/backend`

**"Permission denied"**
→ Run: `chmod +x setup.sh`

**"Can't find .p8 file"**
→ Download it from: https://developer.apple.com/account/resources/authkeys/list

**"Server won't start"**
→ Make sure you ran: `source venv/bin/activate`

**"iPhone not connecting"**
→ Check both devices are on same WiFi

### Detailed Help

- **Full guide**: `STEP_BY_STEP_GUIDE.md`
- **Your checklist**: `YOUR_CHECKLIST.md`
- **Troubleshooting**: `STEP_BY_STEP_GUIDE.md` (bottom section)

---

## 📚 What Each File Does

- `START_HERE.md` ← You are here!
- `YOUR_CHECKLIST.md` - Quick checklist with your info
- `STEP_BY_STEP_GUIDE.md` - Detailed guide with explanations
- `QUICKSTART.md` - 5-minute guide for experienced devs
- `SETUP_GUIDE.md` - Full documentation
- `ARCHITECTURE.md` - How it all works (technical)

---

## 🎯 Your Next Steps

1. **Download your `.p8` file** from Apple Developer Portal
2. **Open Terminal** and run the commands above
3. **Update Xcode** with your server IP
4. **Test on iPhone**
5. **Celebrate!** 🎉

---

**Ready to start?**

→ If you want detailed explanations: Open `STEP_BY_STEP_GUIDE.md`

→ If you just want to get it done: Follow the commands above

→ If you get stuck: Check `STEP_BY_STEP_GUIDE.md` troubleshooting section

**Let's do this!** 🚀
