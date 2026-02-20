#!/bin/bash

echo "🚀 Starting StarCy Backend Server"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Not in backend directory"
    echo "Please run: cd backend"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file first"
    exit 1
fi

# Check if .p8 file exists
if [ ! -f "AuthKey_9KR3NSQZD4.p8" ]; then
    echo "❌ Error: AuthKey_9KR3NSQZD4.p8 not found"
    echo "Please copy your .p8 file to this directory"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "📥 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

echo ""
echo "✅ Configuration:"
echo "   - Key ID: 9KR3NSQZD4"
echo "   - Team ID: 68F8CZM2Q7"
echo "   - Bundle ID: com.star.starcyyy"
echo "   - Server: http://192.0.0.2:8000"
echo ""
echo "🎯 Starting server..."
echo "   (Press Ctrl+C to stop)"
echo ""

python main.py
