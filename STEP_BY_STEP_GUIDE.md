# Step-by-Step Guide for First-Time Setup

## What You're About to Do

You're going to set up a small Python server on your Mac that will send push notifications to your iPhone to keep the Dynamic Island active 24/7. Don't worry - I'll walk you through every single step!

---

## Part 1: Get Your Apple Push Notification Credentials (10 minutes)

### Step 1: Go to Apple Developer Portal

1. Open your web browser
2. Go to: https://developer.apple.com/account/resources/authkeys/list
3. Sign in with your Apple ID (the one you use for development)

### Step 2: Create a New Key

1. You should see a page that says "Keys" at the top
2. Click the **blue + button** (it says "Create a key" when you hover)
3. You'll see a form:
   - **Key Name**: Type `StarCy Push Notifications`
   - **Checkboxes**: Find and CHECK the box that says **"Apple Push Notifications service (APNs)"**
4. Click **Continue** (blue button at top right)
5. Click **Register** (blue button)

### Step 3: Download Your Key File

⚠️ **IMPORTANT**: You can only download this file ONCE. If you lose it, you'll have to create a new key.

1. Click **Download** (blue button)
2. A file named `AuthKey_XXXXXXXXXX.p8` will download to your Downloads folder
3. **Don't close this page yet!** You need to copy some information:

### Step 4: Copy Important Information

On the same page, you'll see:

1. **Key ID**: It looks like `9KR3NSQZD4` (10 characters)
   - Write this down or copy it somewhere safe
   
2. Look at the top right corner of the page - you'll see your name and a code like `68F8CZM2Q7`
   - This is your **Team ID**
   - Write this down too

3. You also need your **Bundle ID**:
   - Open Xcode
   - Click on your project (the blue icon at the top of the file list)
   - Click on "starcy" under TARGETS
   - Look for "Bundle Identifier" - it looks like `com.yourname.starcy`
   - Write this down

**Summary - You should now have:**
- ✅ A file: `AuthKey_XXXXXXXXXX.p8` in your Downloads
- ✅ Key ID: (10 characters, like `9KR3NSQZD4`)
- ✅ Team ID: (10 characters, like `68F8CZM2Q7`)
- ✅ Bundle ID: (like `com.yourname.starcy`)

---

## Part 2: Setup the Backend Server (5 minutes)

### Step 5: Open Terminal

1. Press `Cmd + Space` (opens Spotlight)
2. Type `Terminal`
3. Press Enter

You should see a window with text and a cursor blinking.

### Step 6: Navigate to Your Project

In Terminal, type these commands (press Enter after each one):

```bash
cd ~/Documents/StarCy/starcy-os
```

Then:

```bash
cd backend
```

You should see something like:
```
staryutish@Yutishs-MacBook-Air backend %
```

### Step 7: Run the Setup Script

Type this command:

```bash
./setup.sh
```

You'll see:
- "Creating virtual environment..."
- "Installing dependencies..."
- "Setup complete!"

This installs all the Python packages needed.

### Step 8: Copy Your Key File

Remember that `.p8` file you downloaded? Let's move it here.

Type this command (replace `XXXXXXXXXX` with your actual filename):

```bash
cp ~/Downloads/AuthKey_XXXXXXXXXX.p8 ./
```

**Example**: If your file is `AuthKey_9KR3NSQZD4.p8`, type:
```bash
cp ~/Downloads/AuthKey_9KR3NSQZD4.p8 ./
```

### Step 9: Create Your Configuration File

Type:

```bash
cp .env.example .env
```

Now open the file in a text editor:

```bash
open -a TextEdit .env
```

You'll see a file that looks like this:

```env
# Apple Push Notification Service (APNs) Configuration
APNS_KEY_ID=YOUR_KEY_ID_HERE
APNS_TEAM_ID=YOUR_TEAM_ID_HERE
APNS_BUNDLE_ID=com.yourcompany.starcy
APNS_KEY_PATH=./AuthKey_XXXXXXXXXX.p8

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Environment (development or production)
ENVIRONMENT=development
```

**Now edit it with YOUR information:**

1. Replace `YOUR_KEY_ID_HERE` with your Key ID (like `9KR3NSQZD4`)
2. Replace `YOUR_TEAM_ID_HERE` with your Team ID (like `68F8CZM2Q7`)
3. Replace `com.yourcompany.starcy` with your Bundle ID
4. Replace `AuthKey_XXXXXXXXXX.p8` with your actual filename

**Example of what it should look like:**

```env
APNS_KEY_ID=9KR3NSQZD4
APNS_TEAM_ID=68F8CZM2Q7
APNS_BUNDLE_ID=com.yutish.starcy
APNS_KEY_PATH=./AuthKey_9KR3NSQZD4.p8
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
```

**Save the file** (Cmd + S) and close TextEdit.

---

## Part 3: Start the Server (2 minutes)

### Step 10: Activate Python Environment

In Terminal, type:

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your command line:
```
(venv) staryutish@Yutishs-MacBook-Air backend %
```

### Step 11: Start the Server

Type:

```bash
python main.py
```

You should see:

```
✅ Scheduler started - Dynamic Island will rotate every 20 seconds
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

🎉 **Your server is now running!**

**Don't close this Terminal window** - the server needs to stay running.

---

## Part 4: Find Your Mac's IP Address (1 minute)

### Step 12: Get Your Local IP

Open a **NEW** Terminal window (Cmd + N) and type:

```bash
ipconfig getifaddr en0
```

You'll see something like:
```
192.168.1.100
```

**Write this down** - this is your Mac's IP address on your local network.

---

## Part 5: Update Your iOS App (2 minutes)

### Step 13: Update the Backend URL

1. In Xcode, open the file: `starcy/Core/Services/BackendPushService.swift`
2. Find this line (around line 20):
   ```swift
   private let backendURL = "http://YOUR_SERVER_IP:8000"
   ```
3. Replace `YOUR_SERVER_IP` with your Mac's IP address from Step 12

**Example:**
```swift
private let backendURL = "http://192.168.1.100:8000"
```

4. Save the file (Cmd + S)

---

## Part 6: Test It! (3 minutes)

### Step 14: Build and Run on Your iPhone

⚠️ **IMPORTANT**: You MUST use a **real iPhone**, not the simulator. Push notifications don't work in the simulator.

1. Connect your iPhone to your Mac with a cable
2. In Xcode, select your iPhone from the device dropdown (top left)
3. Click the Play button (▶️) to build and run

### Step 15: Watch the Magic Happen

1. **In Xcode Console** (bottom panel), you should see:
   ```
   📱 Device token received: 1234abcd...
   ✅ Registered with backend
   ```

2. **In Terminal** (where your server is running), you should see:
   ```
   📱 Device registered: 1234abcd... (Activity: xyz789...)
   🔄 Running periodic rotation at 12:34:56
   ✅ Live Activity updated for device 1234abcd...
   ```

3. **On Your iPhone**:
   - You should see the Dynamic Island appear
   - Wait 20 seconds - it should change content
   - **Now close the app completely** (swipe up from bottom, swipe app away)
   - **Watch the Dynamic Island** - it should keep rotating every 20 seconds!

🎉 **IT'S WORKING!** Your Dynamic Island is now active 24/7!

---

## Troubleshooting

### "Device token not received"

**Problem**: Xcode console doesn't show device token.

**Solution**:
1. Make sure you're using a **real iPhone** (not simulator)
2. Check if push notifications are enabled:
   - iPhone Settings → StarCy → Notifications → Allow Notifications (ON)
3. Try restarting the app

### "Backend registration failed"

**Problem**: Can't connect to backend server.

**Solution**:
1. Make sure the server is running (check Terminal window)
2. Test the server: Open Safari and go to `http://192.168.1.100:8000` (use your IP)
   - You should see: `{"status":"running","service":"StarCy Backend",...}`
3. Make sure your iPhone and Mac are on the **same WiFi network**
4. Check the IP address is correct in `BackendPushService.swift`

### "Push notifications not working"

**Problem**: Dynamic Island stops updating.

**Solution**:
1. Check Terminal - are you seeing "✅ Live Activity updated" messages?
2. Check your `.env` file - make sure all values are correct
3. Make sure the `.p8` file is in the `backend/` folder
4. Try restarting the server (Ctrl+C in Terminal, then `python main.py` again)

### "Server won't start"

**Problem**: Error when running `python main.py`

**Solution**:
1. Make sure you activated the virtual environment: `source venv/bin/activate`
2. Check if port 8000 is already in use:
   ```bash
   lsof -i :8000
   ```
   If something is using it, kill it:
   ```bash
   kill -9 [PID]
   ```
3. Try reinstalling dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## What's Happening Behind the Scenes?

1. **Your iPhone** registers with Apple's servers and gets a unique "device token"
2. **Your iPhone** sends this token to your backend server
3. **Your backend server** stores the token and starts a timer
4. **Every 20 seconds**, the server sends a push notification to Apple
5. **Apple** delivers the notification to your iPhone
6. **Your iPhone** receives the notification and updates the Dynamic Island
7. **The Dynamic Island** rotates content (dashboard → news → weather → calendar)

This keeps happening **forever**, even when your app is closed!

---

## Next Steps

### Keep the Server Running

Right now, the server only runs when Terminal is open. To keep it running:

**Option 1: Keep Terminal Open**
- Just leave the Terminal window open
- Your Mac needs to stay on

**Option 2: Deploy to a Cloud Server** (later)
- See `SETUP_GUIDE.md` for deploying to DigitalOcean, AWS, etc.
- Costs $5-10/month
- Server runs 24/7 even when your Mac is off

### Customize Content Rotation

Want to change what shows in the Dynamic Island? Edit `backend/main.py`:

1. Find the `rotate_content_for_device` function (around line 90)
2. Change the `content_types` list
3. Modify the content for each type
4. Restart the server

---

## Summary

✅ You created an APNs key in Apple Developer Portal
✅ You set up a Python backend server on your Mac
✅ You configured the server with your credentials
✅ You updated your iOS app to connect to the server
✅ Your Dynamic Island now rotates 24/7!

**Congratulations!** You just built your first backend server and integrated it with push notifications! 🎉

---

## Need Help?

If you get stuck:
1. Check the error messages in Terminal
2. Check the Xcode console for errors
3. Make sure all the credentials are correct in `.env`
4. Try the troubleshooting section above

**Common mistakes:**
- Using simulator instead of real iPhone ❌
- Wrong IP address in BackendPushService.swift ❌
- Typo in .env file ❌
- Forgot to activate virtual environment ❌
- iPhone and Mac on different WiFi networks ❌
