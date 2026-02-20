#!/bin/bash

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        🚀 StarCy Backend Deployment Wizard 🚀              ║"
echo "║                                                            ║"
echo "║     Real-Time Dynamic Island Updates - 24/7                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "This wizard will help you deploy your backend in 5 minutes."
echo ""

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."
echo ""

# Check if Railway CLI is installed
if command -v railway &> /dev/null; then
    echo "✅ Railway CLI found"
else
    echo "❌ Railway CLI not found"
    echo ""
    read -p "Install Railway CLI now? (y/n): " install_railway
    if [ "$install_railway" = "y" ]; then
        echo "📦 Installing Railway CLI..."
        npm install -g @railway/cli
        echo "✅ Railway CLI installed"
    else
        echo "⚠️  You'll need Railway CLI to continue"
        echo "   Install it with: npm install -g @railway/cli"
        exit 1
    fi
fi

echo ""

# Step 2: Get APNs credentials
echo "🔑 Step 2: APNs Credentials"
echo ""
echo "We need your Apple Push Notification credentials."
echo ""

# Check if .p8 file exists
if [ -f "AuthKey_9KR3NSQZD4.p8" ]; then
    echo "✅ Found APNs key file: AuthKey_9KR3NSQZD4.p8"
    echo ""
    echo "📋 Your APNS_KEY_ID is: 9KR3NSQZD4"
    echo ""
else
    echo "❌ APNs key file not found"
    echo "   Please place AuthKey_9KR3NSQZD4.p8 in this directory"
    exit 1
fi

# Get Team ID
echo "Please enter your Apple Team ID:"
echo "(Find it at: https://developer.apple.com/account > Membership)"
read -p "Team ID: " team_id

if [ -z "$team_id" ]; then
    echo "❌ Team ID is required"
    exit 1
fi

echo ""
echo "✅ Team ID: $team_id"
echo ""

# Generate base64 key
echo "🔐 Generating base64 encoded key..."
apns_key_base64=$(base64 -i AuthKey_9KR3NSQZD4.p8)
echo "✅ Key encoded"
echo ""

# Step 3: Login to Railway
echo "🔐 Step 3: Login to Railway"
echo ""
echo "Opening Railway login in your browser..."
railway login

echo ""

# Step 4: Initialize project
echo "🚀 Step 4: Initialize Railway project"
echo ""
railway init

echo ""

# Step 5: Set environment variables
echo "⚙️  Step 5: Setting environment variables"
echo ""

railway variables set APNS_KEY_ID=9KR3NSQZD4
railway variables set APNS_TEAM_ID=$team_id
railway variables set APNS_BUNDLE_ID=com.star.starcyyy
railway variables set APNS_KEY_BASE64="$apns_key_base64"
railway variables set ENVIRONMENT=production

echo "✅ Environment variables set"
echo ""

# Step 6: Deploy
echo "🚀 Step 6: Deploying to Railway"
echo ""
echo "This may take 2-3 minutes..."
railway up

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              ✅ DEPLOYMENT COMPLETE! ✅                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Get your backend URL:"
echo "   railway domain"
echo ""
echo "2. Update iOS app with your URL:"
echo "   Edit: StarCy-iOS/starcy/Core/Services/BackendPushService.swift"
echo "   Change: private let backendURL = \"https://your-url.up.railway.app\""
echo ""
echo "3. Test your backend:"
echo "   curl https://your-url.up.railway.app/health"
echo ""
echo "4. Rebuild iOS app and test!"
echo ""
echo "📊 View logs:"
echo "   railway logs"
echo ""
echo "🎉 Your Dynamic Island will now update in real-time, even when the app is killed!"
echo ""