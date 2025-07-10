#!/bin/bash

echo "🚀 Building PDF Industrial Pipeline Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building production bundle..."
npm run build

echo "✅ Frontend build complete!"
echo "📁 Build files are in frontend/build/"

# Go back to root directory
cd ..

echo "🎉 Ready to serve! Run 'python main.py' to start the server." 