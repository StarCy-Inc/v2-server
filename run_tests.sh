#!/bin/bash

echo "🧪 StarCy Backend Test Suite"
echo "============================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Test 1: Backend Health
echo "Test 1: Backend Health Check"
echo "-----------------------------"
python diagnose.py
if [ $? -eq 0 ]; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    exit 1
fi

echo ""
echo ""

# Test 2: Registered Devices
echo "Test 2: Registered Devices"
echo "--------------------------"
python test_push.py
echo ""

# Test 3: Scoring System
echo ""
echo "Test 3: Scoring System"
echo "----------------------"
python test_scoring.py
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Scoring system tests passed"
else
    echo ""
    echo "❌ Scoring system tests failed"
    exit 1
fi

echo ""
echo ""
echo "============================"
echo "✅ All automated tests passed!"
echo "============================"
echo ""
echo "📱 Next: Test with your iPhone"
echo ""
echo "1. Open StarCy app on your iPhone"
echo "2. Wait for Dynamic Island to appear"
echo "3. Close the app (swipe up)"
echo "4. Watch Dynamic Island for 2 minutes"
echo "5. Verify it updates every 20 seconds"
echo ""
echo "If iPhone tests pass, you're ready for Railway! 🚀"
echo ""
