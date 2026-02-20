#!/bin/bash

echo "🚀 StarCy Backend Deployment Helper"
echo "===================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

echo "📋 Pre-deployment Checklist:"
echo ""
echo "1. Create a GitHub repository for your backend"
echo "2. Sign up for Railway at https://railway.app"
echo "3. Have your APNs key file ready (AuthKey_9KR3NSQZD4.p8)"
echo "4. Have your Google credentials ready (credentials.json)"
echo ""

read -p "Have you completed the above steps? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please complete the checklist first"
    exit 1
fi

echo ""
echo "🔧 Step 1: Preparing files for deployment..."
echo ""

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
.env
token.json
.DS_Store
*.log
EOF
    echo "✅ .gitignore created"
else
    echo "✅ .gitignore already exists"
fi

# Check if required files exist
echo ""
echo "Checking required files..."
files=("main.py" "requirements.txt" "Procfile" "railway.json" "runtime.txt" "AuthKey_9KR3NSQZD4.p8" "credentials.json")
all_files_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "❌ Some required files are missing. Please add them before deploying."
    exit 1
fi

echo ""
echo "🔐 Step 2: Encoding secret files for Railway..."
echo ""

# Encode APNs key to base64
if [ -f "AuthKey_9KR3NSQZD4.p8" ]; then
    APNS_KEY_BASE64=$(base64 -i AuthKey_9KR3NSQZD4.p8)
    echo "✅ APNs key encoded"
    echo ""
    echo "📋 Copy this value for Railway environment variable APNS_KEY_BASE64:"
    echo "---"
    echo "$APNS_KEY_BASE64"
    echo "---"
    echo ""
fi

# Encode Google credentials to base64
if [ -f "credentials.json" ]; then
    GOOGLE_CREDS_BASE64=$(base64 -i credentials.json)
    echo "✅ Google credentials encoded"
    echo ""
    echo "📋 Copy this value for Railway environment variable GOOGLE_CREDENTIALS_BASE64:"
    echo "---"
    echo "$GOOGLE_CREDS_BASE64"
    echo "---"
    echo ""
fi

echo ""
echo "🔧 Step 3: Initialize Git repository..."
echo ""

if [ -d ".git" ]; then
    echo "✅ Git repository already initialized"
else
    git init
    echo "✅ Git repository initialized"
fi

echo ""
echo "📦 Step 4: Commit files..."
echo ""

git add .
git commit -m "Prepare backend for Railway deployment" || echo "✅ No changes to commit"

echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Create a GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name it 'starcy-backend'"
echo "   - Make it PRIVATE (contains secret files)"
echo "   - Don't initialize with README"
echo ""
echo "2. Push your code to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/starcy-backend.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose 'starcy-backend'"
echo "   - Railway will auto-deploy!"
echo ""
echo "4. Add environment variables in Railway:"
echo "   APNS_KEY_ID=9KR3NSQZD4"
echo "   APNS_TEAM_ID=68F8CZM2Q7"
echo "   APNS_BUNDLE_ID=com.star.starcyyy"
echo "   APNS_KEY_BASE64=<paste the value from above>"
echo "   ENVIRONMENT=production"
echo "   GOOGLE_CREDENTIALS_BASE64=<paste the value from above>"
echo ""
echo "5. Get your Railway URL and update iOS app:"
echo "   - Copy the URL from Railway dashboard"
echo "   - Update BackendPushService.swift with the new URL"
echo ""
echo "🎉 That's it! Your backend will be running 24/7 on Railway!"
echo ""
