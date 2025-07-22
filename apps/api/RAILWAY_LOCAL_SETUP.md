# Railway Local Development Setup

## Overview
This guide helps you connect your local development environment to Railway's production services.

## Getting Public URLs from Railway

Railway's internal URLs (`.railway.internal`) only work inside Railway's network. For local development, you need the public URLs.

### 1. Get PostgreSQL Public URL
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your **API (Arremate360)** project
3. Click on the **PostgreSQL** service
4. Go to the **Connect** tab
5. Copy the **Public Network** connection string
6. It will look like: `postgresql://postgres:[password]@[xxx].railway.app:[port]/railway`

### 2. Get Redis Public URL
1. In the same project, click on the **Redis** service
2. Go to the **Connect** tab
3. Copy the **Public Network** connection string
4. It will look like: `redis://default:[password]@[xxx].railway.app:[port]`

## Setting Up Local Environment

### Option 1: Use Railway Services (Recommended for Testing)
1. Copy `.env.railway-local` to `.env`
2. Update the DATABASE_URL with the PostgreSQL public URL
3. Update the REDIS_URL and CELERY URLs with the Redis public URL

```bash
cp .env.railway-local .env
# Edit .env and replace the internal URLs with public URLs
```

### Option 2: Use Local Services (Recommended for Development)
1. Use the default `.env.development` which uses local PostgreSQL and Redis
2. Install local PostgreSQL and Redis if needed
3. Create local database: `createdb pdf_pipeline_dev`

### Option 3: Use Mock Mode (Quick Start)
1. Use the current `.env` file
2. The API will run in mock mode without database
3. Good for frontend development and testing

## Current Railway Services

Based on your Railway environment:

- **API URL**: https://pdf-industrial-pipeline-production.up.railway.app
- **PostgreSQL**: Available on Railway (need public URL)
- **Redis**: Available on Railway (need public URL)
- **S3 Bucket**: arremate360 (eu-north-1)

## Testing Connection

After setting up your `.env` file:

```bash
# Start the API
npm run dev:api

# Check health endpoint
curl http://localhost:9082/health

# If connected to Railway, you should see:
# "database": "connected"
# "redis": "connected"
```

## Environment Variables Quick Reference

```env
# Railway Production API
RAILWAY_API_URL=https://pdf-industrial-pipeline-production.up.railway.app

# AWS S3 (Already configured)
S3_BUCKET=arremate360
S3_REGION=eu-north-1
AWS_ACCESS_KEY_ID=AKIAS56ATHGV7FBZKHMA
AWS_SECRET_ACCESS_KEY=[in your .env.railway-local]

# Supabase (Already configured)
SUPABASE_URL=https://rjbiyndpxqaallhjmbwm.supabase.co
SUPABASE_ANON_KEY=[in your .env.railway-local]
```

## Troubleshooting

### "role postgres does not exist"
- You're trying to use local PostgreSQL but it's not set up
- Either install PostgreSQL locally or use Railway's database

### "Connection refused"
- The internal Railway URLs don't work locally
- Get the public URLs from Railway dashboard

### Running in Mock Mode
- This is fine for frontend development
- The API will return sample data
- No actual processing will occur