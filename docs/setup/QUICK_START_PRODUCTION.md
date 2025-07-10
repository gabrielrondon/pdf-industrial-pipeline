# 🚀 Quick Start: Production Deployment

Fast-track guide to get your PDF Industrial Pipeline running in production in under 2 hours.

## ⏱️ Time Estimate: 60-75 minutes

### Prerequisites (5 minutes)
- GitHub repository with your code
- Email for service registrations
- Credit card for Railway (free trial available)

## 🎯 Phase 1: Essential Services (25 minutes)

### Database Architecture Overview
You need **3 separate services** for different purposes:
- **Railway PostgreSQL**: Main application database (business data)
- **Railway Redis**: Cache + background job queue (performance)  
- **Supabase**: User authentication + frontend database (user features)

### 1. Railway Setup (15 minutes) - PostgreSQL + Redis + API Hosting
```bash
# Go to https://railway.app
# 1. Sign up with GitHub account
# 2. Click "New Project"
# 3. Click "Deploy PostgreSQL" (this creates your main database)
# 4. Wait for PostgreSQL to deploy (2-3 minutes)
# 5. Click "+" button in your project
# 6. Click "Deploy Redis" (this creates your cache/queue)
# 7. Wait for Redis to deploy (1-2 minutes)

# Get your database URLs:
# - Click on PostgreSQL service → Variables tab
# - Copy the DATABASE_URL (starts with postgresql://)
# - Click on Redis service → Variables tab  
# - Copy the REDIS_URL (starts with redis://)
```

### 2. Supabase Setup (10 minutes) - User Authentication & Frontend DB
```bash
# This manages: user login, profiles, permissions, frontend features
# Go to https://supabase.com
# 1. Create account and new project: "pdf-pipeline-auth"
# 2. Wait for project to be ready (2-3 minutes)
# 3. Go to Settings → API
# 4. Copy your Project URL and anon (public) key
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Execute SQL Schema in Supabase (5 minutes)
```bash
# In Supabase dashboard:
# 1. Go to "SQL Editor" (left sidebar)
# 2. Click "New query"
# 3. Copy and paste this SQL code:
```

```sql
-- Create user profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  plan TEXT DEFAULT 'free',
  credits INTEGER DEFAULT 10,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create documents table for frontend
CREATE TABLE IF NOT EXISTS documents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  title TEXT NOT NULL,
  file_path TEXT,
  analysis_result JSONB,
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create subscriptions table for payments
CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  stripe_subscription_id TEXT UNIQUE,
  plan TEXT NOT NULL,
  status TEXT NOT NULL,
  current_period_start TIMESTAMP WITH TIME ZONE,
  current_period_end TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Create security policies
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own documents" ON documents
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own documents" ON documents
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own subscriptions" ON subscriptions
  FOR SELECT USING (auth.uid() = user_id);
```

```bash
# 4. Click "Run" button (bottom right of SQL editor)
# 5. You should see "Success. No rows returned" for each command
# 6. If you see any errors, check the syntax and try again
```

## 🎯 Phase 2: Payment Processing (20 minutes)

### Stripe Setup
```bash
# Go to https://stripe.com
# 1. Create account and verify business
# 2. Enable BRL currency
# 3. Create products:
#    - Pro Plan: R$ 39.00/month
#    - Premium Plan: R$ 99.00/month
# 4. Get API keys from developers section
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_PUBLISHABLE_KEY="pk_live_..."

# Test with card: 4242 4242 4242 4242
```

## 🎯 Phase 3: Server Setup (25 minutes)

### 1. Install Dependencies (10 minutes)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install Tesseract OCR
sudo apt install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo systemctl start docker
```

### 2. Clone and Setup Project (15 minutes)
```bash
# Clone repository
git clone https://github.com/your-username/pdf-industrial-pipeline.git
cd pdf-industrial-pipeline

# Install dependencies
npm install
cd apps/api && python3.11 -m pip install -r requirements.txt && cd ../..

# Generate secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Create production environment files
cp .env.production.template .env.production
cp apps/client-frontend/.env.production.template apps/client-frontend/.env.production
cp apps/admin-frontend/.env.production.template apps/admin-frontend/.env.production
cp apps/api/.env.production.template apps/api/.env.production
```

## 🎯 Phase 4: Configuration (15 minutes)

### 1. Update Environment Files
```bash
# Edit main .env.production
nano .env.production
# Add your actual values:
# DATABASE_URL=your-neon-url
# REDIS_URL=your-upstash-url
# SECRET_KEY=your-generated-key

# Edit frontend env
nano apps/client-frontend/.env.production
# Add:
# VITE_SUPABASE_URL=your-supabase-url
# VITE_SUPABASE_ANON_KEY=your-anon-key
# VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-key

# Edit API env
nano apps/api/.env.production
# Ensure same DATABASE_URL, REDIS_URL, SECRET_KEY
```

### 2. SSL Certificate (10 minutes)
```bash
# Install Certbot
sudo apt install certbot -y

# Get SSL certificate (replace with your domain)
sudo certbot certonly --standalone -d api.your-domain.com

# Note certificate paths:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

## 🎯 Phase 5: Deploy to Railway (15 minutes)

### 1. Deploy API to Railway (10 minutes)
```bash
# In your Railway project (where you created PostgreSQL and Redis):
# 1. Click "+" button
# 2. Select "Deploy from GitHub repo"
# 3. Connect your GitHub account if needed
# 4. Select your pdf-industrial-pipeline repository
# 5. Railway will start building automatically

# Configure the service:
# 1. Click on your newly created service
# 2. Go to "Settings" tab
# 3. Change "Root Directory" to "apps/api"
# 4. Change "Start Command" to "python main_v2.py"
```

### 2. Configure Environment Variables in Railway (5 minutes)
```bash
# In Railway service → Variables tab, add these:

# Database URLs (use Railway's internal references)
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# Core application settings
SECRET_KEY=your-secret-key-from-env-production
ENVIRONMENT=production
DEBUG=false

# External services (from your existing setup)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
STRIPE_SECRET_KEY=your-stripe-secret-key

# Storage (use local for now)
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/storage

# OCR and processing
TESSERACT_CMD=tesseract
OCR_LANGUAGES=por,eng
API_WORKERS=2
CELERY_WORKER_CONCURRENCY=2
```

### 3. Frontend Deployment (Automatic)
```bash
# Netlify automatically deploys from your git pushes
# Update frontend environment variables to use Railway API URL:

# Get your Railway service URL (looks like: https://service-name.railway.app)
# Update apps/client-frontend/.env.production:
VITE_API_BASE_URL=https://your-service-name.railway.app

# Update apps/admin-frontend/.env.production:
VITE_API_BASE_URL=https://your-service-name.railway.app

# Commit and push to trigger Netlify deployment:
git add .
git commit -m "Update API URLs for Railway deployment"
git push origin main
```

## 🎯 Phase 6: Verification (5 minutes)

### Test Complete Workflow
```bash
# 1. API Health Check
# Go to your Railway service → Settings → Domains
# Copy your service URL (https://xxx.railway.app)
curl https://your-service-name.railway.app/health
# Should return: {"status": "healthy"}

# 2. Check Railway Logs
# In Railway dashboard → your service → Logs tab
# Look for: "Application startup complete"
# No error messages about database connections

# 3. Test Frontend
# Go to your Netlify dashboard
# Find your deployed frontend URLs
# Visit client frontend and try:
# - User registration (tests Supabase)
# - User login (tests Supabase)
# - Upload small PDF (tests Railway API)
# - Check processing status (tests full pipeline)

# 4. Monitor All Services
# Railway: Check that PostgreSQL, Redis, and API are all "Active"
# Supabase: Check that project is running
# Netlify: Check that frontends deployed successfully
```

## 🎯 Essential Monitoring Setup (Bonus - 15 minutes)

### Quick Sentry Setup
```bash
# Go to https://sentry.io
# 1. Create project for Python and React
# 2. Get DSN keys
# 3. Add to environment files:
export SENTRY_DSN="https://your-dsn@sentry.io/project"
```

## 📋 Post-Deployment Checklist

### ✅ Verify These Work:
- [ ] API health endpoint responds
- [ ] User can register/login
- [ ] PDF upload works
- [ ] Payment flow works (test mode)
- [ ] Admin interface accessible
- [ ] SSL certificates valid
- [ ] Monitoring captures errors

### 🔧 Common Issues & Fixes

**Issue: API not starting**
```bash
# Check logs
docker-compose -f apps/api/docker-compose.production.yml logs api

# Common fixes:
# 1. Check DATABASE_URL is correct
# 2. Verify Redis connection
# 3. Ensure Tesseract is installed
```

**Issue: Frontend not loading**
```bash
# Check Netlify deployment logs
# Common fixes:
# 1. Verify environment variables in Netlify
# 2. Check build settings
# 3. Verify API_BASE_URL points to correct domain
```

**Issue: Payment not working**
```bash
# Common fixes:
# 1. Verify Stripe keys match (test vs live)
# 2. Check webhook configuration
# 3. Verify BRL currency enabled
```

## 📞 Getting Help

### Quick Support
- **Documentation**: [docs/README.md](../README.md)
- **API Issues**: Check `docker logs`
- **Frontend Issues**: Check browser console
- **Payment Issues**: Check Stripe dashboard
- **Database Issues**: Check Neon/Supabase dashboard

### Performance Optimization (Later)
- Set up Prometheus + Grafana
- Configure CDN for static assets
- Implement Redis caching
- Add horizontal scaling

## 🎉 Success!

If you've completed all phases, you should have:
- ✅ Full PDF processing pipeline running
- ✅ User authentication working
- ✅ Payment processing active
- ✅ Brazilian judicial analysis available
- ✅ SSL secured endpoints
- ✅ Basic monitoring in place

**Total time**: ~2 hours for a production-ready system!

### Next Steps:
1. **Test thoroughly** with real users
2. **Set up monitoring** dashboards
3. **Configure backups**
4. **Plan scaling** based on usage
5. **Collect user feedback**

**🚀 Your PDF Industrial Pipeline is now live in production!**