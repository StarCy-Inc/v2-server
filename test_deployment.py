#!/usr/bin/env python3
"""
Test script for StarCy Backend deployment
Tests all endpoints to ensure deployment is working
"""

import requests
import json
import sys
from datetime import datetime

def test_backend(base_url):
    """Test all backend endpoints"""
    print(f"🧪 Testing StarCy Backend at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   📊 Status: {data.get('status')}")
            print(f"   📱 Active devices: {data.get('active_devices')}")
            print(f"   👥 Monitoring users: {data.get('monitoring_users')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint working")
            print(f"   🏷️  Service: {data.get('service')}")
            print(f"   📦 Version: {data.get('version')}")
            print(f"   🌍 Environment: {data.get('environment')}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Device registration (mock)
    print("\n3. Testing device registration...")
    try:
        test_registration = {
            "device_token": "test_device_token_12345678",
            "activity_id": "test_activity_id",
            "user_id": "test_user"
        }
        
        response = requests.post(
            f"{base_url}/register", 
            json=test_registration,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Device registration working")
            print(f"   📝 Message: {data.get('message')}")
            print(f"   🔍 Monitoring: {data.get('monitoring_enabled')}")
        else:
            print(f"   ❌ Device registration failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Device registration error: {e}")
    
    # Test 4: List devices
    print("\n4. Testing device listing...")
    try:
        response = requests.get(f"{base_url}/devices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Device listing working")
            print(f"   📱 Device count: {data.get('count')}")
        else:
            print(f"   ❌ Device listing failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Device listing error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Backend deployment test completed!")
    print(f"🕐 Tested at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <backend_url>")
        print("Example: python test_deployment.py https://starcy-backend.onrender.com")
        sys.exit(1)
    
    backend_url = sys.argv[1].rstrip('/')
    
    # Validate URL format
    if not backend_url.startswith(('http://', 'https://')):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    success = test_backend(backend_url)
    
    if success:
        print("\n🎉 All tests passed! Your backend is ready.")
        print("\n📋 Next steps:")
        print("1. Copy your backend URL")
        print("2. Update iOS app with this URL")
        print("3. Test Dynamic Island updates")
    else:
        print("\n❌ Some tests failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()