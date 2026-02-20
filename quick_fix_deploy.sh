#!/bin/bash

echo "🔧 StarCy Backend - Quick Fix & Deploy"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this from the StarCy-iOS/backend directory"
    exit 1
fi

echo "✅ In correct directory"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "🐍 Python version: $python_version"

# Test imports locally
echo "🧪 Testing imports..."
python3 -c "
try:
    import fastapi
    import uvicorn
    import pyjwt
    import httpx
    import apscheduler
    print('✅ Core dependencies OK')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Local import test failed. Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Test the main app
echo "🚀 Testing main app..."
python3 -c "
import sys
sys.path.append('.')
try:
    from main import app
    print('✅ Main app imports successfully')
except Exception as e:
    print(f'❌ Main app error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Main app test failed"
    exit 1
fi

echo ""
echo "✅ All local tests passed!"
echo ""
echo "📋 Ready for deployment:"
echo "1. Go to https://render.com"
echo "2. Create new Web Service from GitHub"
echo "3. Set Root Directory: StarCy-iOS/backend"
echo "4. Build Command: pip install -r requirements.txt"
echo "5. Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "🔑 Environment variables to add:"
echo "   APNS_KEY_ID=9KR3NSQZD4"
echo "   APNS_TEAM_ID=[your_team_id]"
echo "   APNS_BUNDLE_ID=com.star.starcyyy"
echo "   APNS_KEY_BASE64=[your_base64_key]"
echo "   ENVIRONMENT=production"
echo ""
echo "🎉 Your backend is ready to deploy!"