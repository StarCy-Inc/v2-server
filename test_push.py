#!/usr/bin/env python3
"""
Test script to verify backend can send push notifications
This simulates what happens when a device is registered
"""

import asyncio
import httpx

BACKEND_URL = "http://localhost:8000"

async def test_backend():
    """Test backend endpoints"""
    
    print("🧪 Testing StarCy Backend\n")
    
    # Test 1: Health check
    print("1️⃣ Testing health check...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
    
    # Test 2: Check registered devices
    print("2️⃣ Checking registered devices...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/devices")
        data = response.json()
        print(f"   Active devices: {data['count']}")
        if data['devices']:
            for device in data['devices']:
                print(f"   - Device: {device['device_token']}")
                print(f"     Activity ID: {device['activity_id']}")
                print(f"     Last update: {device['last_update']}")
        else:
            print("   ⚠️  No devices registered yet")
            print("   📱 You need to:")
            print("      1. Open the StarCy app on your iPhone")
            print("      2. Make sure Dynamic Island is active")
            print("      3. The app will automatically register with the backend")
        print()
    
    # Test 3: Simulate device registration (for testing only)
    print("3️⃣ Would you like to simulate a device registration? (y/n)")
    print("   Note: This won't actually send push notifications without a real device token")
    print("   But it will show you how the backend handles registration\n")

if __name__ == "__main__":
    asyncio.run(test_backend())
