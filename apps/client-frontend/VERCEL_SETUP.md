# Vercel Deployment Guide

## Quick Setup

### 1. Environment Variables in Vercel
Go to your Vercel project dashboard and add these environment variables:

```env
NODE_ENV=production
VITE_APP_ENV=production
VITE_API_BASE_URL=https://pdf-industrial-pipeline-production.up.railway.app
VITE_SUPABASE_URL=https://rjbiyndpxqaallhjmbwm.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYml5bmRweHFhYWxsaGptYndtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NjEwNzUsImV4cCI6MjA2MTIzNzA3NX0.h3hviSaTY6fJLUrRbl2X6LHfQlxAhHishQ-jVur09-A
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ERROR_REPORTING=true
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from the client-frontend directory
cd apps/client-frontend
vercel --prod
```

### 3. Auto-deployment Setup
- Connect your GitHub repository to Vercel
- Set the build settings:
  - **Framework Preset**: Vite
  - **Build Command**: `npm run build`
  - **Output Directory**: `dist`
  - **Install Command**: `npm install`
  - **Root Directory**: `apps/client-frontend`

## Build Configuration

The project is already optimized for Vercel with:
- ✅ Vite configuration with proper build settings
- ✅ SPA routing with fallback to index.html
- ✅ Environment variable support
- ✅ Production-optimized builds

## Architecture

**Frontend (Vercel)** → **API (Railway)** → **Database (Railway)**

- Frontend hosted on Vercel
- API remains on Railway (no changes needed)
- Database and Redis remain on Railway
- Supabase for authentication only

## Important Notes

1. **API URL**: Make sure `VITE_API_BASE_URL` points to your Railway API
2. **CORS**: Your Railway API already has CORS configured for `*`
3. **Authentication**: Uses Supabase for auth, Railway for document processing
4. **Build Time**: First build may take 2-3 minutes due to dependencies

## Testing Before Deployment

```bash
# Test production build locally
npm run build
npm run preview

# Check if all environment variables are loaded
npm run build:dev
```