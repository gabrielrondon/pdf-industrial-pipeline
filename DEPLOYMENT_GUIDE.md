# Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the PDF Industrial Pipeline to production. The system is designed for high availability, scalability, and security.

## Prerequisites

### Hardware Requirements

**Minimum Production Setup:**
- 4 CPU cores
- 16GB RAM
- 100GB SSD storage
- 1Gbps network connection

**Recommended Production Setup:**
- 8+ CPU cores
- 32GB+ RAM
- 500GB+ SSD storage
- 10Gbps network connection

**High-Scale Production Setup:**
- 16+ CPU cores
- 64GB+ RAM
- 1TB+ NVMe SSD storage
- Load balancer with multiple instances

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Ubuntu 20.04+ / RHEL 8+ / Amazon Linux 2
- SSL certificates for HTTPS

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd pdf-industrial-pipeline

# Copy environment file
cp .env.production.example .env.production

# Edit with your values
nano .env.production
```

### 2. Configure Environment Variables

Fill in all required variables in `.env.production`:

```bash
# Critical security settings
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Database
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/pdf_pipeline

# Storage
S3_BUCKET=your-pdf-storage-bucket
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

### 3. SSL Configuration

```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificates
cp your-domain.crt ssl/
cp your-domain.key ssl/
cp ca-bundle.crt ssl/  # if required

# Or generate self-signed for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/selfsigned.key \
  -out ssl/selfsigned.crt
```

### 4. Deploy

```bash
# Start all services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f app1
```

## Detailed Configuration

### Database Setup

The system uses PostgreSQL with the following optimizations:

```sql
-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_jobs_user_created ON jobs(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_chunks_job_status ON job_chunks(job_id, status);
CREATE INDEX CONCURRENTLY idx_embeddings_model ON embeddings(model_name, model_version);

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX CONCURRENTLY idx_chunks_text_search ON job_chunks USING gin (cleaned_text gin_trgm_ops);
```

### Redis Configuration

Create `redis.production.conf`:

```conf
# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass your-redis-password

# Performance
tcp-keepalive 300
timeout 0
```

### Nginx Configuration

Create `nginx.production.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app_backend {
        least_conn;
        server app1:8000 max_fails=3 fail_timeout=30s;
        server app2:8000 max_fails=3 fail_timeout=30s;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /etc/nginx/ssl/your-domain.crt;
        ssl_certificate_key /etc/nginx/ssl/your-domain.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        
        client_max_body_size 500M;
        
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        location /health {
            access_log off;
            proxy_pass http://app_backend;
        }
    }
    
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }
}
```

## Monitoring Setup

### Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'pdf-pipeline'
    static_configs:
      - targets: ['app1:8000', 'app2:8000']
    metrics_path: /metrics
    scrape_interval: 30s
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
      
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

### Grafana Dashboards

The system includes pre-configured dashboards for:
- Application metrics
- Infrastructure monitoring
- Business metrics
- Error tracking

## Security Configuration

### 1. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP (redirects to HTTPS)
ufw allow 443/tcp     # HTTPS
ufw allow 3000/tcp    # Grafana (restrict to admin IPs)
ufw allow 9090/tcp    # Prometheus (restrict to admin IPs)
ufw enable
```

### 2. SSL/TLS Best Practices

- Use TLS 1.2+ only
- Implement HSTS headers
- Use strong cipher suites
- Regular certificate renewal

### 3. Database Security

```sql
-- Create read-only user for monitoring
CREATE USER monitoring WITH PASSWORD 'secure-password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring;

-- Create application user with limited privileges
CREATE USER app_user WITH PASSWORD 'secure-password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

### 4. Environment Security

- Store secrets in environment variables or secret management
- Use least-privilege principles
- Regular security updates
- Network segmentation

## Scaling Guide

### Horizontal Scaling

#### Application Scaling
```bash
# Scale application instances
docker-compose -f docker-compose.production.yml up -d --scale app1=3 --scale app2=3

# Scale Celery workers
docker-compose -f docker-compose.production.yml up -d --scale celery-pdf=4 --scale celery-ml=2
```

#### Database Scaling
For high-load scenarios:
1. Implement read replicas
2. Use connection pooling (PgBouncer)
3. Consider database sharding for very large datasets

#### Storage Scaling
- Use distributed storage (AWS S3, MinIO cluster)
- Implement CDN for frequently accessed files
- Archive old data to cheaper storage tiers

### Performance Optimization

#### Database Optimization
```sql
-- Regular maintenance
ANALYZE;
REINDEX;
VACUUM FULL;

-- Optimize configurations
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
```

#### Application Optimization
- Enable caching layers
- Optimize ML model loading
- Use batch processing for bulk operations
- Implement request deduplication

## Backup and Recovery

### Automated Backups

The system includes automated backup scripts:

```bash
# Database backup (included in docker-compose)
./scripts/backup.sh

# Storage backup
aws s3 sync s3://pdf-pipeline-storage s3://pdf-pipeline-backups/$(date +%Y%m%d)
```

### Recovery Procedures

#### Database Recovery
```bash
# Restore from backup
docker exec -i postgres_container pg_restore -U postgres -d pdf_pipeline < backup.sql

# Point-in-time recovery
docker exec postgres_container pg_basebackup -U postgres -D /backup -Ft -z -P
```

#### Application Recovery
```bash
# Rolling update
docker-compose -f docker-compose.production.yml up -d --no-deps app1
docker-compose -f docker-compose.production.yml up -d --no-deps app2
```

## Maintenance

### Regular Tasks

1. **Daily:**
   - Monitor application health
   - Check error logs
   - Verify backup completion

2. **Weekly:**
   - Review performance metrics
   - Update security patches
   - Clean up old log files

3. **Monthly:**
   - Review and optimize database
   - Update dependencies
   - Capacity planning review

### Log Management

```bash
# Log rotation
echo '
/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}' > /etc/logrotate.d/pdf-pipeline
```

### Health Checks

The system provides multiple health check endpoints:
- `/health` - Overall application health
- `/health/live` - Liveness probe
- `/health/ready` - Readiness probe
- `/metrics` - Prometheus metrics

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check for memory leaks in ML models
   - Increase worker limits
   - Optimize chunk sizes

2. **Slow Processing**
   - Scale worker processes
   - Optimize database queries
   - Check storage I/O

3. **Database Connection Issues**
   - Increase connection pool size
   - Check network connectivity
   - Review firewall rules

### Debug Commands

```bash
# Check container status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f app1

# Execute commands in container
docker-compose -f docker-compose.production.yml exec app1 bash

# Check resource usage
docker stats

# Database connections
docker-compose -f docker-compose.production.yml exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

## Support

For production support:
1. Check logs first: `docker-compose logs`
2. Review monitoring dashboards
3. Check system resources
4. Review recent changes
5. Consult documentation

## Updates and Maintenance

### Zero-Downtime Deployment

```bash
# 1. Update application image
docker-compose -f docker-compose.production.yml pull

# 2. Rolling update
docker-compose -f docker-compose.production.yml up -d --no-deps app1
# Wait for health check to pass
docker-compose -f docker-compose.production.yml up -d --no-deps app2

# 3. Update workers
docker-compose -f docker-compose.production.yml restart celery-pdf celery-ml celery-analysis
```

### Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec app1 alembic upgrade head
```

This deployment guide ensures a robust, scalable, and secure production environment for the PDF Industrial Pipeline.