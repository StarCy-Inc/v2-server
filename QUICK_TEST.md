# 🚀 Quick Test: Is Everything Working?

## Test 1: Is the backend running?

Run this command:
```bash
cd backend
source venv/bin/activate
python test_push.py
```

**Expected output:**
```
✅ Status: 200
✅ Service: StarCy Backend
✅ Active devices: 0 (will be 1 after you open the app)
```

---

## Test 2: Can your iPhone reach the backend?

**On your iPhone:**

1. Open Safari
2. Go to: `http://192.0.0.2:8000`
3. You should see JSON like:
   ```json
   {
     "status": "running",
     "service": "StarCy Backend",
     "active_devices": 0,
     "environment": "development"
   }
   ```

**If you see this** ✅ → Your iPhone can reach the backend!

**If you get an error** ❌ → Your iPhone and Mac are not on the same network

---

## Test 3: Open the StarCy app

1. **Open StarCy app** on your iPhone
2. **Wait for Dynamic Island to appear**
3. **Check the backend terminal** - you should see:
   ```
   📱 Device registered: <token>...
   ```

**If you see this** ✅ → Registration successful!

**If you don't see this** ❌ → Check:
- Is Dynamic Island showing?
- Are push notifications enabled?
- Is the app using the correct backend URL?

---

## Test 4: Close the app and wait

1. **Close the StarCy app** (swipe up)
2. **Wait 20 seconds**
3. **Look at your Dynamic Island**

**Expected:** Dynamic Island should update with new content every 20 seconds!

**If it updates** ✅ → **SUCCESS! 24/7 Dynamic Island is working!**

**If it doesn't update** ❌ → Check backend logs for errors

---

## Quick Troubleshooting

### iPhone can't reach backend (Test 2 fails)

**Solution:** Make sure both devices are on the same WiFi network

1. On Mac: System Settings → Network → WiFi → Details
2. On iPhone: Settings → WiFi
3. Both should show the same network name

### App doesn't register (Test 3 fails)

**Solution:** Check push notification permissions

1. iPhone Settings → StarCy → Notifications
2. Make sure "Allow Notifications" is ON

### Dynamic Island doesn't update (Test 4 fails)

**Solution:** Check backend logs for APNs errors

Look for lines like:
- ✅ `Live Activity updated for device...` (good!)
- ❌ `Failed to update Live Activity: 400` (bad - APNs error)

If you see errors, the APNs credentials might be wrong.

---

## 🎉 Success Checklist

- [ ] Backend running (Test 1)
- [ ] iPhone can reach backend (Test 2)
- [ ] Device registered (Test 3)
- [ ] Dynamic Island updates when app is closed (Test 4)

**All checked?** → You're ready to deploy! 🚀
