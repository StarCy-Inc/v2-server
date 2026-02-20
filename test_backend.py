#!/usr/bin/env python3
"""
Test script for StarCy Backend Server
Verifies APNs configuration and API endpoints
"""

import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000"

async def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


async def test_device_registration():
    """Test device registration"""
    print("\n🔍 Testing device registration...")
    try:
        test_device = {
            "device_token": "test_token_123456789abcdef",
            "activity_id": "test_activity_abc123",
            "user_id": "test_user"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/register",
                json=test_device
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Device registration passed: {data}")
                return True
            else:
                print(f"❌ Device registration failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Device registration error: {e}")
        return False


async def test_list_devices():
    """Test list devices endpoint"""
    print("\n🔍 Testing list devices...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/devices")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ List devices passed: {data['count']} devices registered")
                return True
            else:
                print(f"❌ List devices failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ List devices error: {e}")
        return False


async def test_device_unregistration():
    """Test device unregistration"""
    print("\n🔍 Testing device unregistration...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/unregister",
                params={"device_token": "test_token_123456789abcdef"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Device unregistration passed: {data}")
                return True
            else:
                print(f"❌ Device unregistration failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Device unregistration error: {e}")
        return False


def check_apns_config():
    """Check APNs configuration"""
    print("\n🔍 Checking APNs configuration...")
    
    required_vars = [
        "APNS_KEY_ID",
        "APNS_TEAM_ID",
        "APNS_BUNDLE_ID",
        "APNS_KEY_PATH"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"❌ Missing: {var}")
        else:
            print(f"✅ Found: {var} = {value[:20]}...")
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("Please configure .env file")
        return False
    
    # Check if .p8 file exists
    key_path = os.getenv("APNS_KEY_PATH")
    if not os.path.exists(key_path):
        print(f"\n❌ APNs key file not found: {key_path}")
        print("Please copy your .p8 file to the backend directory")
        return False
    
    print(f"✅ APNs key file found: {key_path}")
    return True


async def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("StarCy Backend Test Suite")
    print("=" * 60)
    
    # Check configuration first
    if not check_apns_config():
        print("\n❌ Configuration check failed. Please fix configuration before testing.")
        return False
    
    # Test API endpoints
    results = []
    results.append(await test_health_check())
    results.append(await test_device_registration())
    results.append(await test_list_devices())
    results.append(await test_device_unregistration())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running before running tests!")
    print("Run: python main.py\n")
    
    input("Press Enter to continue...")
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
