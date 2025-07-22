#!/bin/bash

echo "🚀 Vercel Deployment Script for PDF Industrial Pipeline"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not installed${NC}"
    echo -e "${YELLOW}Install with: npm install -g vercel${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Vercel CLI found${NC}"

# Check if logged in
if ! vercel whoami &>/dev/null; then
    echo -e "${YELLOW}🔐 Please login to Vercel...${NC}"
    vercel login
fi

echo -e "${GREEN}✅ Logged in to Vercel${NC}"

# Test build first
echo -e "\n${BLUE}🧪 Testing build locally...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed. Please fix errors before deploying.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful${NC}"

# Check environment variables
echo -e "\n${BLUE}📋 Required Environment Variables for Vercel:${NC}"
echo "NODE_ENV=production"
echo "VITE_APP_ENV=production"
echo "VITE_API_BASE_URL=https://pdf-industrial-pipeline-production.up.railway.app"
echo "VITE_SUPABASE_URL=https://rjbiyndpxqaallhjmbwm.supabase.co"
echo "VITE_SUPABASE_ANON_KEY=[from Railway variables]"
echo "VITE_ENABLE_DEBUG=false"
echo "VITE_ENABLE_ANALYTICS=true"

echo -e "\n${YELLOW}⚠️  Make sure these are set in Vercel dashboard before deploying!${NC}"

# Ask for confirmation
read -p "$(echo -e ${BLUE}🚀 Ready to deploy to Vercel? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

# Deploy to Vercel
echo -e "\n${BLUE}🚀 Deploying to Vercel...${NC}"
vercel --prod

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}🎉 Deployment successful!${NC}"
    echo -e "${BLUE}📊 Next steps:${NC}"
    echo "1. Check deployment in Vercel dashboard"
    echo "2. Test all functionality on live site"
    echo "3. Configure custom domain if needed"
    echo "4. Monitor performance metrics"
else
    echo -e "\n${RED}❌ Deployment failed. Check Vercel dashboard for details.${NC}"
    exit 1
fi