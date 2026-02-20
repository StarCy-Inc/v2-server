#!/bin/bash

echo "🚀 Deploying StarCy Backend to Render..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    exit 1
fi

echo "✅ Files verified"

# Check environment variables
echo "🔍 Checking environment variables..."

if [ -z "$APNS_KEY_ID" ]; then
    echo "⚠️  APNS_KEY_ID not set"
else
    echo "✅ APNS_KEY_ID: $APNS_KEY_ID"
fi

if [ -z "$APNS_TEAM_ID" ]; then
    echo "⚠️  APNS_TEAM_ID not set"
else
    echo "✅ APNS_TEAM_ID: $APNS_TEAM_ID"
fi

if [ -z "$APNS_BUNDLE_ID" ]; then
    echo "⚠️  APNS_BUNDLE_ID not set"
else
    echo "✅ APNS_BUNDLE_ID: $APNS_BUNDLE_ID"
fi

if [ -z "$APNS_KEY_BASE64" ]; then
    echo "⚠️  APNS_KEY_BASE64 not set"
    echo "💡 To set it, run: base64 -i AuthKey_9KR3NSQZD4.p8"
else
    echo "✅ APNS_KEY_BASE64: [SET]"
fi

echo ""
echo "📋 Render Deployment Checklist:"
echo "1. ✅ Create Render account at https://render.com"
echo "2. ✅ Connect your GitHub repository"
echo "3. ✅ Create new Web Service"
echo "4. ✅ Set Root Directory: StarCy-iOS/backend"
echo "5. ✅ Set Build Command: pip install -r requirements.txt"
echo "6. ✅ Set Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "7. ✅ Add environment variables:"
echo "   - APNS_KEY_ID=$APNS_KEY_ID"
echo "   - APNS_TEAM_ID=$APNS_TEAM_ID"
echo "   - APNS_BUNDLE_ID=$APNS_BUNDLE_ID"
echo "   - APNS_KEY_BASE64=[your_base64_key]"
echo "   - ENVIRONMENT=production"
echo ""
echo "🔗 After deployment, your backend URL will be:"
echo "   https://your-service-name.onrender.com"
echo ""
echo "✅ Ready to deploy!"