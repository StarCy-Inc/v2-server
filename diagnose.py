#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for StarCy Backend
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000"
APNS_KEY_ID = os.getenv("APNS_KEY_ID")
APNS_TEAM_ID = os.getenv("APNS_TEAM_ID")
APNS_BUNDLE_ID = os.getenv("APNS_BUNDLE_ID")
APNS_KEY_PATH = os.getenv("APNS_KEY_PATH")

async def diagnose():
    """Run comprehensive diagnostics"""
    
    print("=" * 60)
    print("🔍 StarCy Backend Diagnostics")
    print("=" * 60)
    print()
    
    # Check 1: Environment variables
    print("1️⃣ Checking environment variables...")
    checks = {
        "APNS_KEY_ID": APNS_KEY_ID,
        "APNS_TEAM_ID": APNS_TEAM_ID,
        "APNS_BUNDLE_ID": APNS_BUNDLE_ID,
        "APNS_KEY_PATH": APNS_KEY_PATH
    }
    
    all_good = True
    for key, value in checks.items():
        if value:
            print(f"   ✅ {key}: {value}")
        else:
            print(f"   ❌ {key}: NOT SET")
            all_good = False
    print()
    
    # Check 2: APNs key file
    print("2️⃣ Checking APNs key file...")
    if os.path.exists(APNS_KEY_PATH):
        with open(APNS_KEY_PATH, 'r') as f:
            content = f.read()
            if "BEGIN PRIVATE KEY" in content:
                print(f"   ✅ APNs key file exists and is valid")
            else:
                print(f"   ❌ APNs key file exists but format is invalid")
                all_good = False
    else:
        print(f"   ❌ APNs key file not found: {APNS_KEY_PATH}")
        all_good = False
    print()
    
    # Check 3: Backend health
    print("3️⃣ Checking backend health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Backend is running")
                print(f"   📊 Status: {data['status']}")
                print(f"   📊 Active devices: {data['active_devices']}")
                print(f"   📊 Environment: {data['environment']}")
            else:
                print(f"   ❌ Backend returned status {response.status_code}")
                all_good = False
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        all_good = False
    print()
    
    # Check 4: Registered devices
    print("4️⃣ Checking registered devices...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/devices", timeout=5.0)
            data = response.json()
            
            if data['count'] == 0:
                print(f"   ⚠️  No devices registered yet")
                print(f"   📱 To register a device:")
                print(f"      1. Open StarCy app on your iPhone")
                print(f"      2. Make sure Dynamic Island is active")
                print(f"      3. The app will automatically register")
            else:
                print(f"   ✅ {data['count']} device(s) registered")
                for device in data['devices']:
                    print(f"   📱 Device: {device['device_token']}")
                    print(f"      Activity: {device['activity_id']}")
                    print(f"      Last update: {device['last_update']}")
                    print(f"      Has calendar data: {device['has_calendar_data']}")
                    print(f"      Has email data: {device['has_email_data']}")
    except Exception as e:
        print(f"   ❌ Error checking devices: {e}")
        all_good = False
    print()
    
    # Check 5: Google authentication
    print("5️⃣ Checking Google authentication...")
    if os.path.exists("./token.json"):
        print(f"   ✅ Google token file exists")
        print(f"   📊 Backend is fetching real Google data")
    else:
        print(f"   ⚠️  Google token file not found")
        print(f"   📊 Backend will use data from iOS app only")
    print()
    
    # Summary
    print("=" * 60)
    if all_good:
        print("✅ All checks passed!")
        print()
        print("🎯 Next steps:")
        print("   1. Open StarCy app on your iPhone")
        print("   2. Make sure you're on the same WiFi network (192.0.0.2)")
        print("   3. Wait for Dynamic Island to appear")
        print("   4. Check backend logs for device registration")
        print("   5. Close the app and watch Dynamic Island update!")
    else:
        print("❌ Some checks failed - please fix the issues above")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(diagnose())
