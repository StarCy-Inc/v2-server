#!/usr/bin/env python3
"""
Property-Based Tests for Calendar Event Creation Endpoint
Uses Hypothesis for property-based testing

Feature: voice-calendar-events
"""

import os
import sys
import httpx
import asyncio
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TEST_DEVICE_TOKEN = "pbt_test_device_token_123"


# Helper function to make async requests in property tests
def make_request(request_data):
    """Synchronous wrapper for async HTTP request"""
    async def _make_request():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/vapi/create_calendar_event",
                json=request_data,
                timeout=5.0
            )
            return response
    
    return asyncio.run(_make_request())


def setup_test_device():
    """Register test device for property tests"""
    async def _setup():
        test_device = {
            "device_token": TEST_DEVICE_TOKEN,
            "activity_id": "pbt_test_activity",
            "user_id": "pbt_test_user"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/register",
                json=test_device
            )
            return response.status_code == 200
    
    return asyncio.run(_setup())


def cleanup_test_device():
    """Unregister test device"""
    async def _cleanup():
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BACKEND_URL}/unregister",
                params={"device_token": TEST_DEVICE_TOKEN}
            )
    
    asyncio.run(_cleanup())


# Property Test 1.1: Past Date Validation (Property 14)
# **Validates: Requirements 9.1**

@given(
    minutes_in_past=st.integers(min_value=6, max_value=10000)  # More than 5 minutes in the past
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_past_date_validation(minutes_in_past):
    """
    Property 14: Past Date Validation
    
    For any event creation request with a date/time in the past (more than 5 minutes),
    the system should reject the request with a clear error message.
    
    **Validates: Requirements 9.1**
    """
    # Generate a datetime in the past
    past_datetime = datetime.now() - timedelta(minutes=minutes_in_past)
    
    request_data = {
        "device_token": TEST_DEVICE_TOKEN,
        "title": "Past Event Test",
        "datetime": past_datetime.isoformat()
    }
    
    response = make_request(request_data)
    
    # Should return 200 with success=False
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()
    assert not data.get("success"), f"Past date should be rejected, but got success=True"
    assert "past" in data.get("message", "").lower(), f"Error message should mention 'past', got: {data.get('message')}"


# Property Test 1.2: Duration Bounds Validation (Property 15)
# **Validates: Requirements 9.2**

@given(
    duration=st.one_of(
        st.integers(min_value=-1000, max_value=4),  # Too short (< 5 minutes)
        st.integers(min_value=1441, max_value=10000)  # Too long (> 1440 minutes / 24 hours)
    )
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_duration_bounds_invalid(duration):
    """
    Property 15: Duration Bounds Validation (Invalid)
    
    For any event creation request with a duration less than 5 minutes or greater than 24 hours,
    the system should reject the request with a clear error message.
    
    **Validates: Requirements 9.2**
    """
    # Generate a future datetime
    future_datetime = datetime.now() + timedelta(days=1)
    
    request_data = {
        "device_token": TEST_DEVICE_TOKEN,
        "title": "Duration Test Event",
        "datetime": future_datetime.isoformat(),
        "duration_minutes": duration
    }
    
    response = make_request(request_data)
    
    # Should return 200 with success=False
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()
    assert not data.get("success"), f"Invalid duration {duration} should be rejected, but got success=True"
    assert "duration" in data.get("message", "").lower(), f"Error message should mention 'duration', got: {data.get('message')}"


@given(
    duration=st.integers(min_value=5, max_value=1440)  # Valid range: 5 minutes to 24 hours
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_duration_bounds_valid(duration):
    """
    Property 15: Duration Bounds Validation (Valid)
    
    For any event creation request with a duration between 5 minutes and 24 hours (inclusive),
    the system should accept the request.
    
    **Validates: Requirements 9.2**
    """
    # Generate a future datetime
    future_datetime = datetime.now() + timedelta(days=1)
    
    request_data = {
        "device_token": TEST_DEVICE_TOKEN,
        "title": "Valid Duration Test",
        "datetime": future_datetime.isoformat(),
        "duration_minutes": duration
    }
    
    response = make_request(request_data)
    
    # Should return 200 with success=True
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()
    assert data.get("success"), f"Valid duration {duration} should be accepted, but got success=False: {data.get('message')}"


def run_property_tests():
    """Run all property-based tests"""
    print("=" * 70)
    print("Property-Based Tests for Calendar Event Creation")
    print("=" * 70)
    
    # Setup
    print("\n🔧 Setting up test device...")
    if not setup_test_device():
        print("❌ Failed to setup test device")
        return False
    print("✅ Test device registered")
    
    try:
        # Run property tests
        print("\n🔍 Running Property Test 1.1: Past Date Validation (Property 14)")
        print("   Validates: Requirements 9.1")
        test_property_past_date_validation()
        print("✅ Property 14: Past Date Validation - PASSED (20 examples)")
        
        print("\n🔍 Running Property Test 1.2: Duration Bounds Validation - Invalid (Property 15)")
        print("   Validates: Requirements 9.2")
        test_property_duration_bounds_invalid()
        print("✅ Property 15: Duration Bounds (Invalid) - PASSED (20 examples)")
        
        print("\n🔍 Running Property Test 1.2: Duration Bounds Validation - Valid (Property 15)")
        print("   Validates: Requirements 9.2")
        test_property_duration_bounds_valid()
        print("✅ Property 15: Duration Bounds (Valid) - PASSED (20 examples)")
        
        print("\n" + "=" * 70)
        print("✅ All property-based tests passed!")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ Property test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error running property tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        print("\n🧹 Cleaning up test device...")
        cleanup_test_device()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running before running tests!")
    print(f"Backend URL: {BACKEND_URL}")
    print("Run: python main.py\n")
    
    input("Press Enter to continue...")
    
    success = run_property_tests()
    sys.exit(0 if success else 1)
