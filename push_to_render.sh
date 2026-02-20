#!/bin/bash

# Script to push backend code to v2-server repo for Render deployment

echo "🚀 Pushing backend to v2-server repo for Render deployment..."

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if v2-server remote exists
if ! git remote | grep -q "v2-server"; then
    echo "📝 Adding v2-server remote..."
    git remote add v2-server https://github.com/StarCy-Inc/v2-server.git
fi

# Show current status
echo ""
echo "📊 Current status:"
git status --short

# Ask for confirmation
echo ""
read -p "Push to v2-server repo? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

# Push to v2-server
echo ""
echo "📤 Pushing to v2-server..."
git push v2-server star-yutish:main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to v2-server!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Go to https://render.com/dashboard"
    echo "2. Create a new Web Service"
    echo "3. Connect to StarCy-Inc/v2-server repo"
    echo "4. Follow the steps in RENDER_DEPLOY.md"
    echo ""
    echo "📖 Full guide: backend/RENDER_DEPLOY.md"
else
    echo ""
    echo "❌ Push failed. Please check your GitHub credentials and repo access."
    exit 1
fi
