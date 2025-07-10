# 🚂 Railway Deployment Guide

Complete step-by-step guide to deploy your PDF Industrial Pipeline on Railway.

## 🎯 Why Railway?
- **Better for ML**: 1GB+ RAM on starter plan
- **No cold starts**: Services stay warm
- **Built-in database**: PostgreSQL and Redis available
- **Simple pricing**: $5/month starter plan
- **Docker support**: Perfect for Python ML apps

---

## 📋 Pre-Requirements
- [ ] GitHub repository with your code
- [ ] Environment variables ready in `.env.production`
- [ ] Railway account (sign up with GitHub)

---

## 🚀 Step 1: Railway Account Setup (5 minutes)

### 1.1 Create Railway Account
```bash
# Go to https://railway.app
# Click "Sign up with GitHub"
# Connect your GitHub account
# Verify email if prompted
```

### 1.2 Install Railway CLI (Optional but helpful)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

---

## 🗄️ Step 2: Set Up Databases on Railway (10 minutes)

### 2.1 Create New Project
```bash
# On Railway dashboard:
# 1. Click "New Project"
# 2. Choose "Empty Project"
# 3. Name it "pdf-industrial-pipeline"
```

### 2.2 Add PostgreSQL Database
```bash
# In your Railway project:
# 1. Click "+" (Add Service)
# 2. Select "Database" → "PostgreSQL"
# 3. Railway will automatically create and configure it
# 4. Note the connection details (automatically generated)
```

### 2.3 Add Redis Database
```bash
# In your Railway project:
# 1. Click "+" (Add Service) again
# 2. Select "Database" → "Redis"
# 3. Railway will automatically create and configure it
# 4. Note the connection details (automatically generated)
```

### 2.4 Get Database URLs
```bash
# PostgreSQL: Go to PostgreSQL service → Variables
# Copy the DATABASE_URL (starts with postgresql://)

# Redis: Go to Redis service → Variables  
# Copy the REDIS_URL (starts with redis://)
```

---

## 🔧 Step 3: Prepare Your Repository (15 minutes)

### 3.1 Create Railway Configuration
Create `railway.toml` in your project root:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "apps/api/Dockerfile"

[deploy]
startCommand = "python main_v2.py"
healthcheckPath = "/health"
healthcheckTimeout = 300

[variables]
PORT = "8000"
PYTHONPATH = "/app"
```

### 3.2 Create Production Dockerfile for Railway
Create `apps/api/Dockerfile.railway`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/storage /app/uploads /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "main_v2.py"]
```

### 3.3 Update Main Application File
Make sure `apps/api/main_v2.py` reads PORT from environment:
```python
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
```

---

## 🚀 Step 4: Deploy API to Railway (10 minutes)

### 4.1 Deploy from GitHub
```bash
# In Railway project dashboard:
# 1. Click "+" (Add Service)
# 2. Select "GitHub Repo"
# 3. Connect your GitHub account if not already
# 4. Select your pdf-industrial-pipeline repository
# 5. Choose the main branch
```

### 4.2 Configure Build Settings
```bash
# In the service settings:
# 1. Go to "Settings" tab
# 2. Set "Root Directory" to "apps/api"
# 3. Set "Build Command" to "pip install -r requirements.txt"
# 4. Set "Start Command" to "python main_v2.py"
```

### 4.3 Add Environment Variables
```bash
# In Railway service → Variables tab, add:

# Core App Settings
SECRET_KEY=your-secret-key-from-env-production
ENVIRONMENT=production
DEBUG=false

# Database URLs (from Railway databases you created)
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Celery (uses same Redis)
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# External Services (from your .env.production)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
STRIPE_SECRET_KEY=your-stripe-secret-key

# Storage (use local for now, can upgrade to S3 later)
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/storage

# OCR Configuration
TESSERACT_CMD=tesseract
OCR_LANGUAGES=por,eng

# Performance
API_WORKERS=2
CELERY_WORKER_CONCURRENCY=2
```

---

## 🌐 Step 5: Deploy Frontends to Netlify (10 minutes)

### 5.1 Configure Client Frontend for Netlify
Update `apps/client-frontend/.env.production`:
```bash
# API URL will be your Railway service URL
VITE_API_BASE_URL=https://your-service-name.railway.app

# Keep your existing Supabase and Stripe configs
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

### 5.2 Configure Admin Frontend for Netlify
Update `apps/admin-frontend/.env.production`:
```bash
# API URL (same as client)
VITE_API_BASE_URL=https://your-service-name.railway.app
```

### 5.3 Deploy to Netlify
```bash
# Netlify will automatically deploy from your git pushes
# Make sure netlify.toml files are configured in each frontend app
# Check that build commands point to correct directories
```

---

## ✅ Step 6: Verification & Testing (15 minutes)

### 6.1 Check Railway Deployment
```bash
# In Railway dashboard:
# 1. Check that all services are "Active" (green)
# 2. Check logs for any errors
# 3. Get your service URL (will be like https://xxx.railway.app)

# Test API health
curl https://your-service-name.railway.app/health
```

### 6.2 Test Database Connections
```bash
# Check Railway logs for:
# - "Database connected successfully"
# - "Redis connected successfully"
# - No connection errors
```

### 6.3 Test Complete Workflow
```bash
# 1. Visit your Netlify frontend URL
# 2. Register a new account (tests Supabase)
# 3. Upload a small PDF (tests Railway API)
# 4. Check processing status (tests background jobs)
# 5. Verify results display (tests full pipeline)
```

---

## 💰 Railway Pricing & Limits

### Starter Plan ($5/month):
- **1 GB RAM** - Good for moderate usage
- **1 GB disk** - Sufficient for processed files
- **100 GB network** - Plenty for API calls
- **No sleeping** - Always available

### Pro Plan ($20/month):
- **8 GB RAM** - Better for heavy ML workloads
- **100 GB disk** - More storage
- **1 TB network** - High traffic support

### Free Tier (Trial):
- **512 MB RAM** - Limited but good for testing
- **1 GB disk** - Basic testing
- **100 GB network** - Sufficient for development

---

## 🔧 Railway-Specific Optimizations

### 6.1 Environment Variable References
Railway allows referencing other services:
```bash
# Reference PostgreSQL service
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}

# Reference Redis service  
REDIS_URL=${{Redis.REDIS_URL}}

# This automatically handles internal networking
```

### 6.2 Health Check Configuration
Railway will use your `/health` endpoint:
```python
# Make sure this endpoint exists in your FastAPI app
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 6.3 Logging Configuration
Railway captures stdout/stderr:
```python
# Use print() or logging for Railway logs
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Application starting...")
```

---

## 🛠️ Troubleshooting

### Common Railway Issues:

#### Build Failures:
```bash
# Check Railway logs for:
# - Missing requirements.txt
# - Python version issues
# - System package installation failures

# Fix: Update Dockerfile with proper dependencies
```

#### Memory Issues:
```bash
# Symptoms: Process killed, out of memory errors
# Solution: Upgrade to Pro plan or optimize ML models

# Temporary fix: Reduce batch sizes
ML_BATCH_SIZE=16  # Instead of 32
```

#### Connection Issues:
```bash
# Database connection errors
# Check: Environment variables are correctly set
# Verify: ${{PostgreSQL.DATABASE_URL}} format is used
```

#### Deployment Not Updating:
```bash
# Force redeploy:
# 1. Go to Deployments tab in Railway
# 2. Click "Redeploy" on latest deployment
# 3. Or push a new commit to trigger build
```

---

## 🚀 Going Live Checklist

### Before Production:
- [ ] All environment variables set correctly
- [ ] Health check endpoint responding
- [ ] Database migrations completed  
- [ ] SSL certificates active (Railway provides automatically)
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented

### Post-Deployment:
- [ ] Test complete user workflow
- [ ] Monitor Railway metrics
- [ ] Check error logs regularly
- [ ] Set up Railway webhooks for notifications
- [ ] Plan scaling strategy based on usage

---

## 📈 Scaling on Railway

### Vertical Scaling:
```bash
# Upgrade plan for more RAM/CPU
# Railway makes this easy - just change plan
```

### Horizontal Scaling:
```bash
# Add multiple API instances
# Use Railway's built-in load balancing
# Scale databases independently
```

### Cost Optimization:
```bash
# Monitor usage in Railway dashboard
# Right-size your plan based on actual usage
# Use Railway's usage alerts
```

---

**🎉 You're now ready to deploy on Railway! This setup gives you a production-ready, scalable architecture that can handle your PDF processing workload efficiently.**