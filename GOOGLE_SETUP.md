# Google Calendar & Gmail Setup

Your backend now fetches REAL calendar events and emails! Here's how to set it up.

## What You'll Get

✅ **Real calendar events** in Dynamic Island
✅ **Real unread email count**
✅ **Recent email senders and subjects**
✅ **Updates every 5 minutes** automatically
✅ **Works 24/7** even when iOS app is closed

---

## Setup (10 minutes)

### Step 1: Enable Google APIs

1. Go to: https://console.cloud.google.com/
2. Sign in with your Google account
3. Click **"Select a project"** at the top
4. Click **"NEW PROJECT"**
   - Project name: `StarCy Backend`
   - Click **Create**

### Step 2: Enable Calendar and Gmail APIs

1. In the search bar at top, type: `Google Calendar API`
2. Click on **Google Calendar API**
3. Click **ENABLE**
4. Go back (click the back arrow)
5. In the search bar, type: `Gmail API`
6. Click on **Gmail API**
7. Click **ENABLE**

### Step 3: Create OAuth Credentials

1. Click the **☰ menu** (top left)
2. Go to: **APIs & Services** → **Credentials**
3. Click **+ CREATE CREDENTIALS** (top)
4. Select **OAuth client ID**

5. If you see "Configure consent screen":
   - Click **CONFIGURE CONSENT SCREEN**
   - Select **External**
   - Click **CREATE**
   
   Fill in:
   - **App name**: `StarCy Backend`
   - **User support email**: Your email
   - **Developer contact**: Your email
   - Click **SAVE AND CONTINUE**
   
   Scopes page:
   - Click **ADD OR REMOVE SCOPES**
   - Search for: `calendar.readonly`
   - Check: **Google Calendar API** → `.../auth/calendar.readonly`
   - Search for: `gmail.readonly`
   - Check: **Gmail API** → `.../auth/gmail.readonly`
   - Click **UPDATE**
   - Click **SAVE AND CONTINUE**
   
   Test users:
   - Click **+ ADD USERS**
   - Add your Gmail address
   - Click **ADD**
   - Click **SAVE AND CONTINUE**
   
   Summary:
   - Click **BACK TO DASHBOARD**

6. Go back to: **Credentials** (left sidebar)
7. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
8. Application type: **Desktop app**
9. Name: `StarCy Backend`
10. Click **CREATE**

### Step 4: Download Credentials

1. You'll see a popup with your credentials
2. Click **DOWNLOAD JSON**
3. The file will be named something like: `client_secret_XXXXX.json`
4. **Rename it to**: `credentials.json`

### Step 5: Copy to Backend Folder

```bash
# Copy the file to your backend folder
cp ~/Downloads/credentials.json ~/Documents/StarCy/starcy-os/backend/
```

---

## Test It!

### 1. Install New Dependencies

```bash
cd ~/Documents/StarCy/starcy-os/backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Server

```bash
python main.py
```

### 3. Authenticate

The first time you run it, a browser window will open:

1. **Sign in** with your Google account
2. Click **Continue** (it will say "Google hasn't verified this app" - that's okay, it's YOUR app)
3. Click **Continue** again
4. Check both boxes:
   - ✅ See your calendars
   - ✅ Read your email
5. Click **Continue**

You should see:
```
✅ Google authentication successful
🔄 Refreshing Google data...
📅 Next event: Team Meeting at 2:30 PM
📧 Unread emails: 5
✅ Google data refreshed
```

### 4. Test on iPhone

1. Build and run your iOS app
2. Watch the Dynamic Island
3. You should see YOUR REAL calendar events and emails!

---

## How It Works

```
Backend Server
    ↓
Every 5 minutes: Fetch Google Calendar & Gmail
    ↓
Store in cache
    ↓
Every 20 seconds: Send to iPhone via push notification
    ↓
Dynamic Island shows REAL data
```

---

## Troubleshooting

### "credentials.json not found"

Make sure the file is in the backend folder:
```bash
ls ~/Documents/StarCy/starcy-os/backend/credentials.json
```

If not there, copy it:
```bash
cp ~/Downloads/credentials.json ~/Documents/StarCy/starcy-os/backend/
```

### "Google authentication failed"

1. Make sure you enabled both APIs (Calendar and Gmail)
2. Make sure you added yourself as a test user
3. Try deleting `token.json` and authenticating again:
   ```bash
   rm token.json
   python main.py
   ```

### "No calendar events showing"

1. Make sure you have events in your Google Calendar
2. Check the server logs - it should show: `📅 Next event: ...`
3. Wait 20 seconds for the next rotation

### "No emails showing"

1. Make sure you have unread emails in Gmail
2. Check the server logs - it should show: `📧 Unread emails: X`
3. Wait for the email rotation cycle

---

## Security Notes

- ✅ `credentials.json` is in `.gitignore` (won't be committed)
- ✅ `token.json` is in `.gitignore` (won't be committed)
- ✅ OAuth tokens refresh automatically
- ✅ Only YOU can access your data (not shared with anyone)

---

## Optional: Skip Google Setup

If you don't want to set up Google integration right now:

1. The server will still work!
2. It will show dummy data instead of real calendar/emails
3. You can add Google integration later

The server will show:
```
⚠️ Google authentication failed - will use dummy data
```

And continue working with placeholder content.

---

## What's Next?

Once Google is set up:
- Your Dynamic Island shows REAL calendar events
- Updates automatically every 5 minutes
- Works 24/7 even when app is closed
- No need to open the app to refresh!

**Ready to deploy to Railway?** See `RAILWAY_DEPLOY.md` (coming next!)
