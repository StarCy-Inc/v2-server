#!/usr/bin/env python3
"""
Test script for Calendar Event Creation Endpoint
Tests validation, error handling, and request processing
"""

import os
import sys
import httpx
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Test device token
TEST_DEVICE_TOKEN = "test_calendar_device_123456789"


async def setup_test_device():
    """Register a test device for calendar event tests"""
    print("🔧 Setting up test device...")
    try:
        test_device = {
            "device_token": TEST_DEVICE_TOKEN,
            "activity_id": "test_calendar_activity",
            "user_id": "test_user_calendar"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/register",
                json=test_device
            )
            
            if response.status_code == 200:
                print("✅ Test device registered")
                return True
            else:
                print(f"❌ Failed to register test device: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False


async def cleanup_test_device():
    """Unregister test device"""
    print("\n🧹 Cleaning up test device...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/unregister",
                params={"device_token": TEST_DEVICE_TOKEN}
            )
            
            if response.status_code == 200:
                print("✅ Test device unregistered")
                return True
            else:
                print(f"⚠️  Failed to unregister test device: {response.status_code}")
                return False
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")
        return False


async def test_valid_calendar_event():
    """Test creating a valid calendar event"""
    print("\n🔍 Test 1: Valid calendar event creation...")
    try:
        # Create event for tomorrow at 2pm
        tomorrow = datetime.now() + timedelta(days=1)
        event_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        request_data = {
            "device_token": TEST_DEVICE_TOKEN,
            "title": "Team Meeting",
            "datetime": event_datetime.isoformat(),
            "duration_minutes": 60,
            "location": "Conference Room A",
            "description": "Quarterly planning discussion"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/vapi/create_calendar_event",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Valid event creation passed: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Event creation failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


async def test_missing_required_fields():
    """Test validation of required fields"""
    print("\n🔍 Test 2: Missing required fields...")
    
    test_cases = [
        {
            "name": "Missing title",
            "data": {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "",
                "datetime": (datetime.now() + timedelta(days=1)).isoformat()
            }
        },
        {
            "name": "Missing datetime",
            "data": {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Test Event"
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/vapi/create_calendar_event",
                    json=test_case["data"]
                )
                
                # Should fail validation
                if response.status_code == 422 or (response.status_code == 200 and not response.json().get("success")):
                    print(f"  ✅ {test_case['name']}: Correctly rejected")
                    results.append(True)
                else:
                    print(f"  ❌ {test_case['name']}: Should have been rejected")
                    results.append(False)
        except Exception as e:
            print(f"  ❌ {test_case['name']}: Error - {e}")
            results.append(False)
    
    return all(results)


async def test_invalid_datetime_format():
    """Test validation of datetime format"""
    print("\n🔍 Test 3: Invalid datetime format...")
    
    invalid_datetimes = [
        "not-a-date",
        "2024-13-45",  # Invalid month/day
        "tomorrow at 2pm",  # Natural language (not ISO 8601)
        "12/25/2024",  # Wrong format
    ]
    
    results = []
    for invalid_dt in invalid_datetimes:
        try:
            request_data = {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Test Event",
                "datetime": invalid_dt
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/vapi/create_calendar_event",
                    json=request_data
                )
                
                # Should fail validation
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("success") and "datetime" in data.get("message", "").lower():
                        print(f"  ✅ '{invalid_dt}': Correctly rejected")
                        results.append(True)
                    else:
                        print(f"  ❌ '{invalid_dt}': Should have been rejected")
                        results.append(False)
                else:
                    print(f"  ✅ '{invalid_dt}': Correctly rejected (status {response.status_code})")
                    results.append(True)
        except Exception as e:
            print(f"  ❌ '{invalid_dt}': Error - {e}")
            results.append(False)
    
    return all(results)


async def test_past_date_validation():
    """Test validation of past dates (Requirement 9.1)"""
    print("\n🔍 Test 4: Past date validation (Requirement 9.1)...")
    
    # Test event 1 hour in the past
    past_datetime = datetime.now() - timedelta(hours=1)
    
    try:
        request_data = {
            "device_token": TEST_DEVICE_TOKEN,
            "title": "Past Event",
            "datetime": past_datetime.isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/vapi/create_calendar_event",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("success") and "past" in data.get("message", "").lower():
                    print(f"✅ Past date correctly rejected: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Past date should have been rejected")
                    return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


async def test_duration_bounds_validation():
    """Test validation of duration bounds (Requirement 9.2)"""
    print("\n🔍 Test 5: Duration bounds validation (Requirement 9.2)...")
    
    tomorrow = datetime.now() + timedelta(days=1)
    event_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    test_cases = [
        {
            "name": "Duration too short (2 minutes)",
            "duration": 2,
            "should_fail": True
        },
        {
            "name": "Duration at minimum (5 minutes)",
            "duration": 5,
            "should_fail": False
        },
        {
            "name": "Duration normal (60 minutes)",
            "duration": 60,
            "should_fail": False
        },
        {
            "name": "Duration at maximum (1440 minutes / 24 hours)",
            "duration": 1440,
            "should_fail": False
        },
        {
            "name": "Duration too long (1500 minutes / 25 hours)",
            "duration": 1500,
            "should_fail": True
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            request_data = {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Duration Test Event",
                "datetime": event_datetime.isoformat(),
                "duration_minutes": test_case["duration"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/vapi/create_calendar_event",
                    json=request_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get("success")
                    
                    if test_case["should_fail"]:
                        if not success and "duration" in data.get("message", "").lower():
                            print(f"  ✅ {test_case['name']}: Correctly rejected")
                            results.append(True)
                        else:
                            print(f"  ❌ {test_case['name']}: Should have been rejected")
                            results.append(False)
                    else:
                        if success:
                            print(f"  ✅ {test_case['name']}: Correctly accepted")
                            results.append(True)
                        else:
                            print(f"  ❌ {test_case['name']}: Should have been accepted - {data.get('message')}")
                            results.append(False)
                else:
                    print(f"  ❌ {test_case['name']}: Unexpected status {response.status_code}")
                    results.append(False)
        except Exception as e:
            print(f"  ❌ {test_case['name']}: Error - {e}")
            results.append(False)
    
    return all(results)


async def test_invalid_device_token():
    """Test validation of device token"""
    print("\n🔍 Test 6: Invalid device token...")
    
    tomorrow = datetime.now() + timedelta(days=1)
    event_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    try:
        request_data = {
            "device_token": "invalid_device_token_xyz",
            "title": "Test Event",
            "datetime": event_datetime.isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/vapi/create_calendar_event",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("success") and "device" in data.get("message", "").lower():
                    print(f"✅ Invalid device token correctly rejected: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Invalid device token should have been rejected")
                    return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


async def test_default_duration():
    """Test default duration of 60 minutes"""
    print("\n🔍 Test 7: Default duration (60 minutes)...")
    
    tomorrow = datetime.now() + timedelta(days=1)
    event_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    try:
        # Don't specify duration_minutes
        request_data = {
            "device_token": TEST_DEVICE_TOKEN,
            "title": "Default Duration Event",
            "datetime": event_datetime.isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/vapi/create_calendar_event",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ Default duration accepted: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Request failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


async def test_optional_fields():
    """Test optional location and description fields"""
    print("\n🔍 Test 8: Optional fields (location, description)...")
    
    tomorrow = datetime.now() + timedelta(days=1)
    event_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    test_cases = [
        {
            "name": "With location only",
            "data": {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Event with Location",
                "datetime": event_datetime.isoformat(),
                "location": "Conference Room B"
            }
        },
        {
            "name": "With description only",
            "data": {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Event with Description",
                "datetime": event_datetime.isoformat(),
                "description": "Important meeting about project updates"
            }
        },
        {
            "name": "With both location and description",
            "data": {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Full Event",
                "datetime": event_datetime.isoformat(),
                "location": "Main Office",
                "description": "Quarterly review meeting"
            }
        },
        {
            "name": "Without optional fields",
            "data": {
                "device_token": TEST_DEVICE_TOKEN,
                "title": "Minimal Event",
                "datetime": event_datetime.isoformat()
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BACKEND_URL}/vapi/create_calendar_event",
                    json=test_case["data"]
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"  ✅ {test_case['name']}: Accepted")
                        results.append(True)
                    else:
                        print(f"  ❌ {test_case['name']}: Failed - {data.get('message')}")
                        results.append(False)
                else:
                    print(f"  ❌ {test_case['name']}: Status {response.status_code}")
                    results.append(False)
        except Exception as e:
            print(f"  ❌ {test_case['name']}: Error - {e}")
            results.append(False)
    
    return all(results)


async def run_tests():
    """Run all calendar event tests"""
    print("=" * 70)
    print("Calendar Event Creation Endpoint Test Suite")
    print("=" * 70)
    
    # Setup
    if not await setup_test_device():
        print("\n❌ Failed to setup test device. Aborting tests.")
        return False
    
    # Run tests
    results = []
    results.append(await test_valid_calendar_event())
    results.append(await test_missing_required_fields())
    results.append(await test_invalid_datetime_format())
    results.append(await test_past_date_validation())
    results.append(await test_duration_bounds_validation())
    results.append(await test_invalid_device_token())
    results.append(await test_default_duration())
    results.append(await test_optional_fields())
    
    # Cleanup
    await cleanup_test_device()
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
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
    print(f"Backend URL: {BACKEND_URL}")
    print("Run: python main.py\n")
    
    input("Press Enter to continue...")
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
