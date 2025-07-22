#!/bin/bash

echo "🧹 Cleaning up development processes..."

# Kill any existing development processes
echo "Killing existing processes..."
pkill -f "vite.*client-frontend" 2>/dev/null || true
pkill -f "vite.*admin-frontend" 2>/dev/null || true  
pkill -f "python3.*main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "concurrently" 2>/dev/null || true

# Wait for processes to terminate
sleep 2

# Check if ports are now free
echo "Checking ports..."
if lsof -i :9080 >/dev/null 2>&1; then
    echo "⚠️  Port 9080 still in use"
    lsof -i :9080
else
    echo "✅ Port 9080 is free"
fi

if lsof -i :9081 >/dev/null 2>&1; then
    echo "⚠️  Port 9081 still in use"
    lsof -i :9081
else
    echo "✅ Port 9081 is free"
fi

if lsof -i :9082 >/dev/null 2>&1; then
    echo "⚠️  Port 9082 still in use"
    lsof -i :9082
else
    echo "✅ Port 9082 is free"
fi

echo "✅ Cleanup complete!"