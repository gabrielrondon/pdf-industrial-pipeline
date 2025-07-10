# 🗄️ Database Architecture Guide

Understanding the 3-database architecture of the PDF Industrial Pipeline.

## 🎯 Why 3 Databases?

The system uses **3 separate databases** for optimal performance, security, and functionality:

### 1. 🐘 PostgreSQL - Main Application Database
### 2. ⚡ Redis - Cache & Job Queue  
### 3. 🔐 Supabase - Authentication & Frontend Database

---

## 🐘 PostgreSQL (Main Database)

### **Purpose**: Core business data storage
### **What it stores**:
```sql
-- Document processing jobs
jobs (id, file_path, status, created_at, results)

-- ML analysis results  
ml_analysis (job_id, model_predictions, confidence_scores)

-- Judicial analysis data
judicial_analysis (job_id, legal_compliance, risk_assessment)

-- System configuration
settings (key, value, environment)

-- Performance metrics
metrics (timestamp, api_response_time, processing_time)
```

### **Service Options**:
- **Neon.tech** (free tier) - Recommended for starting
- **AWS RDS** (~$30/month) - Production ready
- **Google Cloud SQL** (~$25/month) - Alternative
- **Self-hosted** - Full control

### **Configuration**:
```bash
DATABASE_URL="postgresql://user:password@host:5432/pdf_pipeline_prod"
```

---

## ⚡ Redis (Cache & Queue)

### **Purpose**: Performance optimization and background processing
### **What it handles**:

#### Cache Layer:
```bash
# API response caching
"api:response:upload:hash123" → cached_response
"api:response:status:job456" → job_status

# ML model caching
"ml:model:embeddings:hash789" → model_weights
"ml:predictions:doc456" → prediction_results
```

#### Job Queue (Celery):
```bash
# Background processing queues
"celery:pdf_processing" → [job1, job2, job3]
"celery:ml_analysis" → [analysis_task1, analysis_task2]
"celery:judicial_processing" → [legal_task1]
```

#### Session Storage:
```bash
# User sessions and real-time data
"session:user123" → session_data
"notification:user456" → pending_notifications
```

### **Service Options**:
- **Upstash** (free tier) - Serverless Redis
- **AWS ElastiCache** (~$25/month) - Managed Redis
- **Google Memorystore** (~$30/month) - Alternative
- **Self-hosted** - Docker container

### **Configuration**:
```bash
REDIS_URL="redis://user:password@host:6379/0"
CELERY_BROKER_URL="${REDIS_URL}"
CELERY_RESULT_BACKEND="${REDIS_URL}"
```

---

## 🔐 Supabase (Authentication & Frontend)

### **Purpose**: User management and frontend-specific features
### **What it provides**:

#### Authentication:
```sql
-- Built-in auth.users table (managed by Supabase)
auth.users (id, email, encrypted_password, created_at)

-- Custom user profiles
profiles (
  id UUID REFERENCES auth.users(id),
  full_name TEXT,
  plan TEXT DEFAULT 'free',
  credits INTEGER DEFAULT 10
)
```

#### Frontend Features:
```sql
-- Document sharing and permissions
documents (
  id UUID,
  user_id UUID REFERENCES profiles(id),
  title TEXT,
  is_public BOOLEAN DEFAULT false,
  analysis_result JSONB
)

-- Subscription management  
subscriptions (
  id UUID,
  user_id UUID REFERENCES profiles(id),
  stripe_subscription_id TEXT,
  plan TEXT,
  status TEXT
)
```

#### Real-time Features:
- Live document processing updates
- User notification system
- Collaborative document sharing
- Real-time dashboard metrics

### **Service Options**:
- **Supabase.com** (managed service) - Recommended
- **Self-hosted Supabase** - Advanced setup

### **Configuration**:
```bash
SUPABASE_URL="https://project-id.supabase.co"
SUPABASE_ANON_KEY="eyJhbGci..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."
```

---

## 🔄 Data Flow Architecture

### Document Processing Flow:
```mermaid
graph TD
    A[User uploads PDF] --> B[Supabase Auth Check]
    B --> C[FastAPI Backend]
    C --> D[PostgreSQL: Create Job Record]
    C --> E[Redis: Queue Processing Task]
    E --> F[Celery Worker: Process PDF]
    F --> G[PostgreSQL: Store Results]
    F --> H[Redis: Cache Results]
    G --> I[Supabase: Update User Dashboard]
```

### User Authentication Flow:
```mermaid
graph TD
    A[User Login] --> B[Supabase Authentication]
    B --> C[JWT Token Generated]
    C --> D[Frontend Stores Token]
    D --> E[API Calls with Token]
    E --> F[Backend Validates Token]
    F --> G[Access PostgreSQL Data]
    F --> H[Cache in Redis]
```

---

## 📊 Database Responsibilities

| Database | Primary Use | Data Type | Access Pattern |
|----------|-------------|-----------|----------------|
| **PostgreSQL** | Business Logic | Structured, ACID-compliant | Complex queries, transactions |
| **Redis** | Performance | Key-value, temporary | High-frequency, low-latency |
| **Supabase** | User Features | Structured + Real-time | User-centric, real-time updates |

---

## 🔧 Configuration Examples

### Environment Variables Setup:
```bash
# PostgreSQL (Main Database)
DATABASE_URL="postgresql://pdf_user:secure_password@neon-db.com:5432/pdf_pipeline"

# Redis (Cache & Queue)  
REDIS_URL="redis://:redis_password@upstash.com:6379/0"

# Supabase (Auth & Frontend)
SUPABASE_URL="https://abcdefgh.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Connection Pool Configuration:
```python
# PostgreSQL connection pool
DATABASE_POOL_SIZE=20
DATABASE_POOL_TIMEOUT=30

# Redis connection pool
REDIS_MAX_CONNECTIONS=10
REDIS_SOCKET_TIMEOUT=30

# Supabase (managed automatically)
```

---

## 🚀 Scaling Considerations

### PostgreSQL Scaling:
- **Vertical**: Increase CPU/RAM for complex queries
- **Horizontal**: Read replicas for read-heavy workloads
- **Partitioning**: Split large tables by date/user

### Redis Scaling:
- **Memory**: Increase memory for larger cache
- **Clustering**: Redis cluster for high availability
- **Separate instances**: Different Redis instances for cache vs queue

### Supabase Scaling:
- **Plan upgrade**: Higher limits and better performance
- **Edge functions**: Serverless processing closer to users
- **Real-time scaling**: More concurrent connections

---

## 💰 Cost Optimization

### Free Tier Setup (Development):
```bash
# Neon PostgreSQL: Free (1GB)
# Upstash Redis: Free (10K commands/day)  
# Supabase: Free (50MB database, 2 GB bandwidth)
# Total: $0/month
```

### Production Setup:
```bash
# Neon Pro: $30/month (10GB)
# Upstash Pro: $25/month (100K commands/day)
# Supabase Pro: $25/month (8GB database, 250 GB bandwidth)
# Total: ~$80/month
```

### Enterprise Setup:
```bash
# AWS RDS Multi-AZ: $150/month
# AWS ElastiCache Cluster: $100/month
# Supabase Enterprise: $100/month
# Total: ~$350/month
```

---

## 🔒 Security Best Practices

### PostgreSQL Security:
- [ ] Use connection pooling with limited connections
- [ ] Enable SSL/TLS encryption
- [ ] Regular security updates
- [ ] Restrict database user permissions
- [ ] Enable audit logging

### Redis Security:
- [ ] Use password authentication
- [ ] Disable dangerous commands in production
- [ ] Use SSL/TLS for connections
- [ ] Network isolation (VPC)
- [ ] Regular memory usage monitoring

### Supabase Security:
- [ ] Enable Row Level Security (RLS)
- [ ] Use service role key only in backend
- [ ] Configure CORS properly
- [ ] Enable audit logs
- [ ] Regular access key rotation

---

## 🛠️ Troubleshooting

### Common Issues:

#### PostgreSQL Connection Issues:
```bash
# Test connection
psql $DATABASE_URL -c "SELECT version();"

# Check pool exhaustion
# Look for "remaining connection slots are reserved" errors
```

#### Redis Connection Issues:
```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping

# Check memory usage
redis-cli -u $REDIS_URL info memory
```

#### Supabase Issues:
```bash
# Test Supabase connection
curl "$SUPABASE_URL/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY"

# Check authentication
# Look for "JWT expired" or "Invalid JWT" errors
```

---

## 📈 Monitoring

### Key Metrics to Track:

#### PostgreSQL:
- Connection pool usage
- Query performance (slow queries)
- Database size growth
- Transaction rates

#### Redis:
- Memory usage
- Cache hit rates
- Queue lengths
- Eviction rates

#### Supabase:
- API request rates
- Authentication success rates
- Real-time connection counts
- Storage usage

---

**This 3-database architecture provides optimal performance, security, and scalability for the PDF Industrial Pipeline while keeping costs manageable.**