# 🔧 External Services Setup Guide

Complete step-by-step instructions for setting up all external services required for production deployment.

## 📋 Service Setup Order

Follow this order for optimal setup experience:
1. [Database Services](#1-database-services) (PostgreSQL, Redis)
2. [Storage Services](#2-storage-services) (AWS S3 or MinIO)
3. [Authentication](#3-authentication-supabase) (Supabase)
4. [Payment Processing](#4-payment-processing-stripe) (Stripe)
5. [Monitoring Stack](#5-monitoring-stack) (Optional but recommended)
6. [AI Services](#6-ai-services-optional) (Optional)

---

## 1. Database Services

### PostgreSQL Database Setup

#### Option A: Managed PostgreSQL (Recommended)

**AWS RDS:**
```bash
# 1. Go to AWS Console → RDS
# 2. Click "Create database"
# 3. Choose PostgreSQL
# 4. Select version 15.x or higher
# 5. Choose db.t3.micro for testing, db.t3.small+ for production
# 6. Set master username and password
# 7. Note the endpoint URL
```

**Google Cloud SQL:**
```bash
# 1. Go to Google Cloud Console → SQL
# 2. Click "Create Instance"
# 3. Choose PostgreSQL
# 4. Select version 15 or higher
# 5. Choose region closest to your users
# 6. Set instance ID and password
# 7. Note the connection string
```

**Neon (Serverless PostgreSQL):**
```bash
# 1. Go to https://neon.tech
# 2. Sign up for free account
# 3. Create new project
# 4. Choose region
# 5. Get connection string from dashboard
```

#### Option B: Self-Hosted PostgreSQL

**Using Docker:**
```bash
# Create PostgreSQL container
docker run --name pdf-postgres \
  -e POSTGRES_DB=pdf_pipeline_prod \
  -e POSTGRES_USER=pdf_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:15

# Verify connection
docker exec -it pdf-postgres psql -U pdf_user -d pdf_pipeline_prod
```

#### Database Configuration
```bash
# Your connection string will look like:
DATABASE_URL="postgresql://pdf_user:your_secure_password@your-host:5432/pdf_pipeline_prod"
```

### Redis Setup

#### Option A: Managed Redis (Recommended)

**AWS ElastiCache:**
```bash
# 1. Go to AWS Console → ElastiCache
# 2. Click "Create Redis cluster"
# 3. Choose cluster mode disabled
# 4. Select node type (cache.t3.micro for testing)
# 5. Set cluster name
# 6. Note the endpoint URL
```

**Google Memorystore:**
```bash
# 1. Go to Google Cloud Console → Memorystore
# 2. Click "Create instance"
# 3. Choose Redis
# 4. Set instance ID and region
# 5. Choose memory size (1GB minimum)
# 6. Note the IP address
```

#### Option B: Self-Hosted Redis

**Using Docker:**
```bash
# Create Redis container
docker run --name pdf-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  -d redis:7-alpine \
  redis-server --appendonly yes --requirepass your_redis_password

# Test connection
docker exec -it pdf-redis redis-cli -a your_redis_password ping
```

#### Redis Configuration
```bash
# Your Redis URL will look like:
REDIS_URL="redis://:your_redis_password@your-host:6379/0"
```

---

## 2. Storage Services

### AWS S3 Setup

#### Step 1: Create S3 Bucket
```bash
# 1. Go to AWS Console → S3
# 2. Click "Create bucket"
# 3. Choose unique bucket name: "your-company-pdf-pipeline"
# 4. Select region
# 5. Block public access (keep default)
# 6. Enable versioning (recommended)
# 7. Create bucket
```

#### Step 2: Create IAM User
```bash
# 1. Go to AWS Console → IAM
# 2. Click "Users" → "Add user"
# 3. Set username: "pdf-pipeline-s3-user"
# 4. Select "Programmatic access"
# 5. Attach policy "AmazonS3FullAccess" (or create custom policy below)
# 6. Note Access Key ID and Secret Access Key
```

#### Step 3: Custom IAM Policy (More Secure)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-company-pdf-pipeline",
                "arn:aws:s3:::your-company-pdf-pipeline/*"
            ]
        }
    ]
}
```

#### S3 Configuration
```bash
S3_BUCKET="your-company-pdf-pipeline"
S3_REGION="us-east-1"
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="your-secret-key"
```

### MinIO Setup (S3 Alternative)

#### Self-Hosted MinIO
```bash
# Create MinIO container
docker run --name pdf-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=your_secure_password \
  -v minio_data:/data \
  -d quay.io/minio/minio server /data --console-address ":9001"

# Access MinIO Console at http://localhost:9001
# Create bucket named "pdf-pipeline"
```

#### MinIO Configuration
```bash
S3_BUCKET="pdf-pipeline"
S3_REGION="us-east-1"
AWS_ACCESS_KEY_ID="minioadmin"
AWS_SECRET_ACCESS_KEY="your_secure_password"
S3_ENDPOINT_URL="http://minio:9000"
```

---

## 3. Authentication (Supabase)

### Supabase Project Setup

#### Step 1: Create Project
```bash
# 1. Go to https://supabase.com
# 2. Sign up for account
# 3. Click "New project"
# 4. Choose organization
# 5. Set project name: "pdf-pipeline-prod"
# 6. Set database password
# 7. Choose region closest to users
# 8. Create project
```

#### Step 2: Configure Authentication
```bash
# 1. Go to Authentication → Settings
# 2. Configure providers you want to use:
#    - Email (required)
#    - Google (optional)
#    - GitHub (optional)
# 3. Set Site URL: https://your-domain.com
# 4. Add Redirect URLs:
#    - https://your-domain.com/auth/callback
#    - https://admin.your-domain.com/auth/callback
```

#### Step 3: Set Up Row Level Security (RLS)
```sql
-- Enable RLS on profiles table
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy for users to see only their own data
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

-- Policy for users to update their own data
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);
```

#### Step 4: Create Database Schema
```sql
-- Run this in Supabase SQL Editor
-- Users profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  plan TEXT DEFAULT 'free',
  credits INTEGER DEFAULT 10,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id),
  title TEXT NOT NULL,
  file_path TEXT,
  analysis_result JSONB,
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions table
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
```

#### Supabase Configuration
```bash
VITE_SUPABASE_URL="https://your-project-id.supabase.co"
VITE_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 4. Payment Processing (Stripe)

### Stripe Account Setup

#### Step 1: Create Stripe Account
```bash
# 1. Go to https://stripe.com
# 2. Sign up for account
# 3. Complete business verification
# 4. Enable Brazilian Real (BRL) currency
# 5. Set up bank account for payouts
```

#### Step 2: Create Products and Prices
```bash
# 1. Go to Stripe Dashboard → Products
# 2. Create "Pro Plan" product:
#    - Name: Pro Plan
#    - Description: Advanced PDF analysis with 500 credits/month
#    - Price: R$ 39.00 monthly recurring
# 3. Create "Premium Plan" product:
#    - Name: Premium Plan  
#    - Description: Unlimited PDF analysis
#    - Price: R$ 99.00 monthly recurring
# 4. Note the Price IDs (price_xxxxx)
```

#### Step 3: Configure Webhooks
```bash
# 1. Go to Stripe Dashboard → Developers → Webhooks
# 2. Click "Add endpoint"
# 3. Set endpoint URL: https://your-api-domain.com/webhooks/stripe
# 4. Select events to send:
#    - customer.subscription.created
#    - customer.subscription.updated
#    - customer.subscription.deleted
#    - invoice.payment_succeeded
#    - invoice.payment_failed
# 5. Note the webhook signing secret
```

#### Step 4: Test Payment Flow
```bash
# Use Stripe test cards:
# Success: 4242 4242 4242 4242
# Declined: 4000 0000 0000 0002
# 3D Secure: 4000 0000 0000 3220
```

#### Stripe Configuration
```bash
STRIPE_SECRET_KEY="sk_live_..." # Use sk_test_ for testing
STRIPE_PUBLISHABLE_KEY="pk_live_..." # Use pk_test_ for testing
STRIPE_WEBHOOK_SECRET="whsec_..."
STRIPE_PRO_PRICE_ID="price_..."
STRIPE_PREMIUM_PRICE_ID="price_..."
```

---

## 5. Monitoring Stack

### Prometheus Setup

#### Using Docker
```bash
# Create prometheus.yml config
cat > prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'pdf-pipeline-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
EOF

# Run Prometheus
docker run --name pdf-prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  -d prom/prometheus
```

### Grafana Setup

#### Using Docker
```bash
# Run Grafana
docker run --name pdf-grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=your_grafana_password \
  -v grafana_data:/var/lib/grafana \
  -d grafana/grafana

# Access at http://localhost:3000
# Username: admin, Password: your_grafana_password
```

#### Grafana Configuration
```bash
# 1. Add Prometheus data source:
#    URL: http://prometheus:9090
# 2. Import dashboard for FastAPI monitoring
# 3. Create alerts for critical metrics
```

### Sentry Error Tracking (Optional)

#### Step 1: Create Sentry Project
```bash
# 1. Go to https://sentry.io
# 2. Sign up for account
# 3. Create new project
# 4. Choose Python (for API) and React (for frontend)
# 5. Get DSN from project settings
```

#### Sentry Configuration
```bash
SENTRY_DSN="https://your-sentry-dsn@sentry.io/project-id"
SENTRY_ENVIRONMENT="production"
```

---

## 6. AI Services (Optional)

### OpenAI API Setup

#### Step 1: Create OpenAI Account
```bash
# 1. Go to https://platform.openai.com
# 2. Sign up for account
# 3. Add billing information
# 4. Go to API Keys section
# 5. Create new API key
# 6. Set usage limits
```

#### OpenAI Configuration
```bash
OPENAI_KEY="sk-..."
OPENAI_ORG_ID="org-..."
```

### Anthropic Claude API Setup

#### Step 1: Get API Access
```bash
# 1. Go to https://console.anthropic.com
# 2. Request API access
# 3. Once approved, create API key
# 4. Set usage limits
```

#### Anthropic Configuration
```bash
ANTHROPIC_KEY="sk-ant-..."
```

---

## 7. Domain and SSL Setup

### Domain Configuration

#### Step 1: Configure DNS
```bash
# Set up DNS records:
# A record: your-domain.com → your-server-ip
# A record: api.your-domain.com → your-server-ip
# A record: admin.your-domain.com → your-server-ip
# CNAME: www.your-domain.com → your-domain.com
```

#### Step 2: SSL Certificate
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com -d api.your-domain.com -d admin.your-domain.com

# Certificates will be saved to:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

#### Step 3: Auto-renewal
```bash
# Add to crontab for auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

---

## 8. System Dependencies

### Install Required Packages

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Tesseract OCR
sudo apt install tesseract-ocr tesseract-ocr-por tesseract-ocr-eng -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### CentOS/RHEL
```bash
# Install Python 3.11
sudo dnf install python3.11 python3.11-pip -y

# Install Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install nodejs -y

# Install Tesseract OCR
sudo dnf install tesseract tesseract-langpack-por tesseract-langpack-eng -y

# Install Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

---

## 9. Configuration Validation

### Environment Variables Checklist

#### Core Services (Required)
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `REDIS_URL` - Redis connection string
- [ ] `SECRET_KEY` - Generated with `openssl rand -hex 32`
- [ ] `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- [ ] `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`

#### Storage (Recommended)
- [ ] `S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- [ ] `S3_REGION`

#### Monitoring (Optional)
- [ ] `SENTRY_DSN`
- [ ] Prometheus and Grafana passwords

#### AI Services (Optional)
- [ ] `OPENAI_KEY`
- [ ] `ANTHROPIC_KEY`

### Test Connections
```bash
# Test database connection
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"

# Test Redis connection
redis-cli -u $REDIS_URL ping

# Test S3 connection
aws s3 ls s3://$S3_BUCKET --endpoint-url=$S3_ENDPOINT_URL

# Test Tesseract
tesseract --version
```

---

## 10. Security Checklist

### Essential Security Steps
- [ ] Change all default passwords
- [ ] Use strong, unique passwords (16+ characters)
- [ ] Enable 2FA on all service accounts
- [ ] Rotate API keys regularly
- [ ] Set up firewall rules
- [ ] Enable SSL/TLS everywhere
- [ ] Configure backup encryption
- [ ] Set up monitoring alerts
- [ ] Review and limit IAM permissions
- [ ] Enable audit logging

### Network Security
```bash
# Basic firewall setup (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw --force enable
```

---

## 🎯 Next Steps

After completing this setup:

1. **Test Each Service**: Verify all connections work
2. **Deploy Applications**: Follow the deployment guide
3. **Configure Monitoring**: Set up alerts and dashboards
4. **Run Tests**: Execute the full test suite
5. **Go Live**: Switch to production mode

For deployment instructions, see: [Production Deployment Guide](../deployment/DEPLOYMENT_GUIDE.md)