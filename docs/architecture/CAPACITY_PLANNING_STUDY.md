# Capacity Planning Study - Railway Hobby Plan Analysis

*Last Updated: January 2025*

## Executive Summary

This document provides a comprehensive analysis of the PDF Industrial Pipeline capacity under Railway's **Hobby Plan** ($5/month with 8GB RAM / 8 vCPU). The analysis covers processing architecture, memory usage patterns, concurrent user capacity, and scaling recommendations.

## Railway Plan Analysis

### Current Plan: Railway Hobby ($5/month)
- **RAM**: 8GB per service
- **CPU**: 8 vCPU per service  
- **Storage**: 5GB volume storage + 10GB ephemeral
- **Team**: Single developer workspace
- **Usage Credit**: $5 included monthly
- **Support**: Community support

### Upgrade Path: Railway Pro ($20/month)
- **RAM**: 32GB per service (4x increase)
- **CPU**: 32 vCPU per service (4x increase)
- **Storage**: 250GB volume storage
- **Team**: Unlimited seats
- **Usage Credit**: $20 included monthly
- **Support**: Priority support

## Processing Architecture

### Client-Side vs Server-Side Processing

**Client-Side (Browser):**
- ❌ **NO PDF processing** occurs in user browsers
- ✅ **File upload only** (validation + progress monitoring)
- ✅ **Minimal memory usage**: ~10-20MB for upload interface
- ✅ **No processing burden** on end users

**Server-Side (Railway Infrastructure):**
- ✅ **ALL PDF processing** happens on Railway servers
- ✅ **Complete pipeline**: Upload → Chunking → OCR → ML → Analysis
- ✅ **Memory usage**: Occurs entirely on OUR Railway infrastructure
- ✅ **User impact**: Zero processing load on client devices

### Data Flow Architecture

```
User Browser → Railway API → Background Processing → Storage
     ↓              ↓              ↓                    ↓
File Upload    Job Creation   Celery Workers      PostgreSQL
(10-20MB)      (Database)     (500-700MB RAM)    Redis Cache
                                                  File Storage
```

## Memory Usage Analysis

### Per 100MB File Processing

**Memory Consumption Breakdown:**
- **Upload Processing**: ~200MB RAM (2x file size temporarily)
- **PDF Chunking**: ~50MB RAM per active chunk
- **OCR Processing**: ~100-150MB RAM per page being processed
- **ML Analysis**: ~200MB RAM for feature extraction & predictions
- **Database Operations**: ~50MB RAM for data persistence
- **Peak Usage**: ~500-700MB RAM per 100MB file

### Background System Requirements

**Base System Usage:**
- **FastAPI Application**: ~150MB RAM
- **Celery Workers** (4 workers): ~400MB RAM baseline
- **Redis Cache**: ~100MB RAM
- **Database Connections**: ~50MB RAM
- **System Overhead**: ~300MB RAM
- **Total Baseline**: ~1GB RAM

## Capacity Calculations

### Hobby Plan Capacity (8GB RAM)

**Available Processing RAM**: 8GB - 1GB (baseline) = 7GB

**Concurrent File Processing:**
- **Conservative Estimate**: 8-10 files (100MB each) simultaneously
- **Optimistic Estimate**: 12-15 files simultaneously
- **Processing Time**: 2-5 minutes per 100MB file
- **Queue Management**: Additional files wait in queue

### Throughput Analysis

**Daily Processing Capacity:**
- **24/7 Operation**: ~2,000-3,000 files per day
- **Business Hours** (12h): ~1,000-1,500 files per day
- **Peak Hours** (4h): ~400-600 files per day

**Monthly Capacity:**
- **Continuous Processing**: ~60,000-90,000 files per month
- **Realistic Usage**: ~15,000-25,000 files per month

## User Capacity Analysis

### Concurrent Users

**Active Users (uploading):**
- **Simultaneous uploaders**: 50-100 users
- **Processing queue**: 8-15 files at once
- **Average wait time**: 5-15 minutes during peak

### Monthly User Capacity by Usage Pattern

**Light Users** (5 files/user/month):
- **Capacity**: ~3,000-5,000 users
- **Revenue Potential**: $150-250K/month at $50/user

**Moderate Users** (20 files/user/month):
- **Capacity**: ~750-1,250 users  
- **Revenue Potential**: $75-125K/month at $100/user

**Heavy Users** (100 files/user/month):
- **Capacity**: ~150-250 users
- **Revenue Potential**: $75-125K/month at $500/user

**Enterprise Users** (500 files/user/month):
- **Capacity**: ~30-50 users
- **Revenue Potential**: $150-250K/month at $5000/user

## Storage Analysis

### Database Storage (PostgreSQL)

**Per Processed File:**
- **Text Content**: ~2-5MB (extracted text + chunks)
- **Analysis Results**: ~1-3MB (ML predictions + judicial analysis)  
- **Metadata**: ~0.1MB (job info, user data, timestamps)
- **Total per file**: ~5-10MB database storage

**8GB Database Capacity**: ~800-1,600 processed files stored

### File Storage

**Current Setup (Local Railway Storage):**
- **Original PDFs**: 100MB per file
- **Processing Artifacts**: ~50MB per file (chunks, images)
- **Total per file**: ~150MB file storage
- **5GB limit**: ~33 large files stored simultaneously

**Optimization Strategy:**
- **Immediate**: Delete processing artifacts after completion
- **Short-term**: Implement file retention policy (30-90 days)
- **Long-term**: Migrate to S3 for unlimited, cost-effective storage

**S3 Migration Ready**: Complete enterprise-grade S3 backend already implemented. Migration requires only changing environment variables. Full details in `docs/architecture/S3_MIGRATION_PLAN.md`.

## Performance Characteristics

### Processing Times by File Size

**Small Files** (<10MB):
- **Processing Time**: 30-60 seconds
- **Memory Usage**: ~200-300MB peak
- **User Experience**: Near real-time

**Medium Files** (10-50MB):
- **Processing Time**: 1-3 minutes
- **Memory Usage**: ~300-500MB peak  
- **User Experience**: Acceptable wait time

**Large Files** (50-100MB):
- **Processing Time**: 3-8 minutes
- **Memory Usage**: ~500-700MB peak
- **User Experience**: Requires progress indication

### System Bottlenecks

**Primary Bottlenecks:**
1. **RAM Availability**: Limits concurrent processing
2. **OCR Processing**: CPU-intensive, 30-60 seconds per page
3. **File Storage**: 5GB limit requires active management
4. **Database Growth**: Long-term storage planning needed

**Secondary Bottlenecks:**
1. **Network I/O**: Large file uploads
2. **ML Inference**: GPU would accelerate processing
3. **Database Writes**: High volume during bulk processing

## Scaling Strategies

### Optimization Within Hobby Plan

**Immediate Optimizations:**
1. **Increase Celery workers** to 6-8 (from current 4)
2. **Implement file size tiers** (different processing for <10MB vs >50MB)
3. **Add file compression** for storage optimization
4. **Optimize ML models** for memory efficiency

**File Management:**
1. **Automatic cleanup** of processing artifacts
2. **File retention policies** (delete after 30-90 days)
3. **Compress stored files** using ZIP/GZIP
4. **Migrate to S3** for unlimited, cost-effective storage

**IMPORTANT**: The system is already 100% prepared for S3 migration with a complete enterprise-grade implementation. See detailed migration plan in `docs/architecture/S3_MIGRATION_PLAN.md` for:
- Zero-downtime migration process (5 minutes setup)
- Cost analysis showing 87% savings at scale
- Complete storage backend already implemented
- Migration triggers and rollback procedures

### When to Upgrade to Pro Plan

**Upgrade Triggers:**
- **Consistent** >15 concurrent processing jobs
- **Regular** RAM exhaustion warnings
- **User complaints** about processing delays
- **Monthly revenue** >$1,000 (ROI positive for $20/month plan)

**Pro Plan Benefits:**
- **4x RAM capacity**: 32GB vs 8GB
- **4x concurrent processing**: 60-80 files vs 15 files
- **4x user capacity**: 12,000-20,000 vs 3,000-5,000 users
- **Priority support**: Faster issue resolution

## Cost Analysis

### Current Costs (Hobby Plan)

**Monthly Costs:**
- **Railway Hobby**: $5/month
- **Additional usage**: $0-10/month (if exceeding $5 credit)
- **Total**: $5-15/month

**Per-File Costs:**
- **Processing cost**: $0.0002-0.001 per file
- **Storage cost**: Included in plan
- **Very scalable**: Costs grow linearly with usage

### Revenue Requirements

**Break-even Analysis:**
- **Hobby Plan**: Need $15/month revenue (3x cost)
- **Pro Plan**: Need $60/month revenue (3x cost)

**User Pricing Strategy:**
- **Freemium**: 5 files/month free, $10/month for 50 files
- **Professional**: $50/month for 500 files
- **Enterprise**: $500/month for 5,000 files

## Monitoring & Alerts

### Key Metrics to Track

**System Performance:**
- **RAM usage**: Alert at >80% (6.4GB)
- **Processing queue depth**: Alert at >20 files
- **Average processing time**: Track degradation
- **Error rates**: Monitor failures

**Business Metrics:**
- **Files processed per day**: Growth tracking
- **User adoption rate**: Monthly active users
- **Revenue per user**: Pricing optimization
- **Customer satisfaction**: Processing time complaints

### Recommended Alerts

**Critical Alerts:**
- RAM usage >90% for >5 minutes
- Processing queue >30 files
- Error rate >5% over 1 hour
- Database storage >90% full

**Warning Alerts:**
- RAM usage >80% for >15 minutes
- Average processing time >10 minutes
- Queue depth >15 files for >30 minutes

## Recommendations

### Short-term (0-3 months)
1. **Optimize current setup** within Hobby plan limits
2. **Implement file retention** policies
3. **Add comprehensive monitoring** and alerts
4. **Test performance** under various load scenarios

### Medium-term (3-12 months)
1. **Migrate to S3 storage** for cost efficiency
2. **Implement user tiers** and pricing strategy
3. **Add load balancing** for better distribution
4. **Consider Pro plan upgrade** when revenue supports it

### Long-term (12+ months)
1. **Microservices architecture** for better scaling
2. **Multi-region deployment** for global users
3. **GPU acceleration** for ML processing
4. **Enterprise features** for high-value customers

## Conclusion

The Railway Hobby plan at $5/month provides excellent value for the PDF Industrial Pipeline, supporting:

- **3,000-5,000 light users** or **150-250 heavy users**
- **15,000-25,000 files per month** processing capacity
- **Strong ROI potential** with minimal infrastructure costs
- **Clear upgrade path** to Pro plan when needed

The architecture is well-designed for the Hobby plan constraints, with efficient memory usage and scalable processing patterns. The main recommendation is to implement proper monitoring and file retention policies to maximize the plan's effectiveness.

---

*This analysis should be reviewed monthly and updated as usage patterns evolve.*