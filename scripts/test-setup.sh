#!/bin/bash

echo "🧪 Testing complete development setup..."

# Cleanup first
./scripts/cleanup-dev.sh

echo ""
echo "Starting all applications..."
npm run dev &
SETUP_PID=$!

# Wait for services to start
echo "Waiting for services to start..."
sleep 15

echo ""
echo "=== Testing Services ==="

# Test API
echo "1. Testing API Health:"
API_STATUS=$(curl -s http://localhost:9082/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$API_STATUS" = "healthy" ]; then
    echo "   ✅ API is healthy"
else
    echo "   ❌ API health check failed"
fi

# Test Client Frontend
echo "2. Testing Client Frontend:"
CLIENT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9080/)
if [ "$CLIENT_STATUS" = "200" ]; then
    echo "   ✅ Client frontend responding (http://localhost:9080)"
else
    echo "   ❌ Client frontend not responding"
fi

# Test Admin Frontend
echo "3. Testing Admin Frontend:"
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9081/)
if [ "$ADMIN_STATUS" = "200" ]; then
    echo "   ✅ Admin frontend responding (http://localhost:9081)"
else
    echo "   ❌ Admin frontend not responding"
fi

# Test API endpoints
echo "4. Testing API Endpoints:"
JOBS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:9082/api/v1/jobs?user_id=test")
if [ "$JOBS_STATUS" = "200" ]; then
    echo "   ✅ Jobs endpoint working"
else
    echo "   ❌ Jobs endpoint failed"
fi

# Test file upload
echo "5. Testing File Upload:"
echo "Test content" > /tmp/test-upload.txt
UPLOAD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:9082/api/v1/upload -F "file=@/tmp/test-upload.txt" -F "user_id=test")
rm -f /tmp/test-upload.txt
if [ "$UPLOAD_STATUS" = "200" ]; then
    echo "   ✅ Upload endpoint working"
else
    echo "   ⚠️  Upload endpoint returned status $UPLOAD_STATUS (expected for non-PDF)"
fi

echo ""
echo "=== Test Complete ==="
echo "Services are running. Press Ctrl+C to stop them."
echo ""
echo "URLs:"
echo "  🌐 Client Frontend: http://localhost:9080"
echo "  🔧 Admin Frontend: http://localhost:9081"
echo "  🚀 API Documentation: http://localhost:9082/docs"

# Wait for user to stop
wait $SETUP_PID