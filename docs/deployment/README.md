# 🚀 Deployment Documentation

*Production deployment and operations guides*

## 📋 Available Documentation

### 🚀 Quick Start
- **[Production Deployment](production.md)** - Complete production setup guide
- **[Monitoring Setup](monitoring.md)** - System monitoring and alerting
- **[Backup & Recovery](backup.md)** - Data protection strategies

### 📊 Stage Completion Reports
- **[Stage 7 Completion](STAGE7_COMPLETION_SUMMARY.md)** - Frontend integration milestone
- **[Stage 8 Completion](STAGE8_COMPLETION_SUMMARY.md)** - Production deployment milestone

## 🐳 Docker Deployment

### Quick Start
```bash
# Production deployment
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose ps
docker-compose logs -f app
```

### Container Architecture
```
┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│   Load Balance  │
│    (Port 80)    │    │   (3 instances) │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  FastAPI App    │    │     Redis       │
│ (3 replicas)    │────│   (Cache/Queue) │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   File Storage  │    │   Monitoring    │
│   (Persistent)  │    │ (Prometheus)    │
└─────────────────┘    └─────────────────┘
```

## ⚙️ Production Configuration

### Environment Setup
```bash
# Production environment variables
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# Security
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-domain.com
SECRET_KEY=your-super-secret-key

# Database
REDIS_HOST=redis
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# Storage
STORAGE_BACKEND=s3  # or local
AWS_BUCKET_NAME=your-bucket
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Monitoring
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
```

### Docker Compose Production
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

  app:
    build: .
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    environment:
      - ENVIRONMENT=production
      - REDIS_HOST=redis
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 1G

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  redis_data:
```

## 📊 Monitoring & Observability

### Health Monitoring
```bash
# System health endpoints
GET /health                    # Basic health check
GET /performance/system/health # Detailed system status
GET /performance/cache/stats   # Cache performance
GET /metrics                   # Prometheus metrics
```

### Key Metrics
- **Response Time**: API endpoint latency
- **Throughput**: Requests per second
- **Error Rate**: Failed requests percentage
- **Resource Usage**: CPU, memory, disk
- **Queue Length**: Redis job queue size
- **Cache Hit Rate**: Redis cache efficiency

### Alerting Rules
```yaml
# prometheus-alerts.yml
groups:
  - name: pdf-pipeline
    rules:
      - alert: HighErrorRate
        expr: error_rate > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected

      - alert: HighMemoryUsage
        expr: memory_usage > 0.85
        for: 5m
        labels:
          severity: warning
```

## 🔒 Security Configuration

### SSL/TLS Setup
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    location / {
        proxy_pass http://pdf_pipeline;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Configuration
```bash
# UFW rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Block direct app access
sudo ufw deny 6379/tcp   # Block direct Redis access
sudo ufw enable
```

## 📈 Scaling Strategies

### Horizontal Scaling
```yaml
# Docker Swarm mode
version: '3.8'
services:
  app:
    image: pdf-pipeline:latest
    deploy:
      replicas: 5
      update_config:
        parallelism: 2
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### Auto-Scaling Rules
- **CPU > 70%**: Scale up by 1 instance
- **Memory > 80%**: Scale up by 1 instance
- **Queue > 100 jobs**: Scale up by 2 instances
- **Response time > 500ms**: Scale up by 1 instance

## 💾 Backup & Recovery

### Data Backup
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Redis data
redis-cli --rdb /backup/redis_$DATE.rdb

# Backup file storage
tar -czf /backup/storage_$DATE.tar.gz storage/

# Backup configuration
cp -r config/ /backup/config_$DATE/

# Upload to S3
aws s3 sync /backup/ s3://your-backup-bucket/
```

### Recovery Procedures
```bash
# Restore from backup
docker-compose down
redis-cli flushall
redis-cli --rdb < /backup/redis_latest.rdb
tar -xzf /backup/storage_latest.tar.gz
docker-compose up -d
```

## 🔧 Maintenance

### Regular Tasks
- **Daily**: Check logs for errors
- **Weekly**: Review performance metrics
- **Monthly**: Update dependencies
- **Quarterly**: Security audit

### Update Procedures
```bash
# Zero-downtime deployment
docker-compose pull
docker-compose up -d --no-deps --build app
docker-compose logs -f app
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Backup system tested
- [ ] Monitoring dashboards setup
- [ ] Load testing completed
- [ ] Security scan passed

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring alerts active
- [ ] Performance metrics normal
- [ ] User acceptance testing
- [ ] Documentation updated
- [ ] Team notification sent 