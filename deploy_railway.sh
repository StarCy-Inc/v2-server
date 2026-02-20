#!/bin/bash

echo "🚀 StarCy Backend - Railway Deployment"
echo "======================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "✅ Railway CLI found"
echo ""

# Login to Railway
echo "🔐 Logging in to Railway..."
railway login

echo ""
echo "🚀 Deploying backend..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to Railway dashboard: https://railway.app/dashboard"
echo "2. Click on your project"
echo "3. Go to 'Variables' tab"
echo "4. Add these environment variables:"
echo "   - APNS_KEY_ID"
echo "   - APNS_TEAM_ID"
echo "   - APNS_BUNDLE_ID=com.star.starcyyy"
echo "   - APNS_KEY_BASE64 (run: base64 -i AuthKey_9KR3NSQZD4.p8)"
echo "   - ENVIRONMENT=production"
echo ""
echo "5. Copy your backend URL from Railway"
echo "6. Update BackendPushService.swift with the URL"
echo ""