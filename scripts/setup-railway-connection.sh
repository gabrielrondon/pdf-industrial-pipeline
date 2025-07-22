#!/bin/bash

echo "🚂 Railway Connection Setup Helper"
echo "=================================="
echo ""

# Check if Railway CLI is installed and logged in
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not installed"
    echo "Install with: brew install railway"
    exit 1
fi

if ! railway whoami &>/dev/null; then
    echo "❌ Not logged in to Railway"
    echo "Run: railway login"
    exit 1
fi

echo "✅ Railway CLI ready"
echo ""

# Check current project
echo "📁 Current Railway project:"
railway status | head -3
echo ""

echo "🔧 Setup Options:"
echo "1. Use Railway services (PostgreSQL + Redis from Railway)"
echo "2. Use local services (PostgreSQL + Redis on your machine)"
echo "3. Use mock mode (No database needed)"
echo ""

echo "📋 Next Steps:"
echo ""
echo "For Option 1 (Railway services):"
echo "1. Go to https://railway.app/dashboard"
echo "2. Select 'API (Arremate360)' project"
echo "3. Get public URLs for PostgreSQL and Redis"
echo "4. Copy apps/api/.env.railway-local to apps/api/.env"
echo "5. Update DATABASE_URL and REDIS_URL with public URLs"
echo ""
echo "For Option 2 (Local services):"
echo "1. Install PostgreSQL: brew install postgresql"
echo "2. Install Redis: brew install redis"
echo "3. Start services: brew services start postgresql redis"
echo "4. Create database: createdb pdf_pipeline_dev"
echo "5. Use apps/api/.env.development"
echo ""
echo "For Option 3 (Mock mode):"
echo "1. Use the current apps/api/.env file"
echo "2. Comment out DATABASE_URL line"
echo "3. The API will run without database"
echo ""

# Show current Railway variables (without sensitive data)
echo "📊 Your Railway services:"
echo "- API: https://pdf-industrial-pipeline-production.up.railway.app"
echo "- PostgreSQL: Available (get public URL from dashboard)"
echo "- Redis: Available (get public URL from dashboard)"
echo "- S3 Bucket: arremate360 (eu-north-1)"
echo ""

echo "🚀 To start development:"
echo "npm run dev"