#!/bin/bash

echo "🚀 Pushing Fixed Backend to v2-server Repository"
echo "================================================"

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from StarCy-iOS/backend directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ In backend directory"

# Get GitHub username
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "❌ GitHub username is required"
    exit 1
fi

echo "📋 Repository: https://github.com/$github_username/v2-server"

# Ask for confirmation
read -p "Is this correct? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ Cancelled"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
fi

# Add all files
echo "📁 Adding all files..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "⚠️  No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Fixed backend deployment - ready for Render

- Updated requirements.txt with uvicorn[standard]
- Added runtime.txt for Python 3.11.7
- Improved error handling for Google services
- Added deployment test scripts
- Ready for production deployment"
fi

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "🔗 Remote origin already exists"
    current_remote=$(git remote get-url origin)
    echo "Current remote: $current_remote"
    
    expected_remote="https://github.com/$github_username/v2-server.git"
    if [ "$current_remote" != "$expected_remote" ]; then
        echo "🔄 Updating remote URL..."
        git remote set-url origin $expected_remote
    fi
else
    echo "🔗 Adding remote origin..."
    git remote add origin https://github.com/$github_username/v2-server.git
fi

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
if git push -u origin main; then
    echo ""
    echo "✅ SUCCESS! Backend pushed to v2-server repository"
    echo ""
    echo "🔗 Repository URL: https://github.com/$github_username/v2-server"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to https://render.com"
    echo "2. Create new Web Service"
    echo "3. Connect to your v2-server repository"
    echo "4. Use these settings:"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "5. Add environment variables:"
    echo "   - APNS_KEY_ID=9KR3NSQZD4"
    echo "   - APNS_TEAM_ID=[your_team_id]"
    echo "   - APNS_BUNDLE_ID=com.star.starcyyy"
    echo "   - APNS_KEY_BASE64=[your_base64_key]"
    echo "   - ENVIRONMENT=production"
    echo ""
    echo "🎉 Your backend is ready to deploy!"
else
    echo ""
    echo "❌ Push failed. Common solutions:"
    echo "1. Make sure the v2-server repository exists on GitHub"
    echo "2. Check your GitHub credentials"
    echo "3. Try: git push --set-upstream origin main"
    echo ""
    echo "Manual commands:"
    echo "git remote -v  # Check remote URL"
    echo "git status     # Check git status"
    echo "git push origin main  # Try push again"
fi